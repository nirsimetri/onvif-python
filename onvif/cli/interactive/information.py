"""Information commands implementation."""

from __future__ import annotations

import cmd
from typing import Callable

from requests.exceptions import RequestException
from zeep.exceptions import TransportError

from onvif.cli.helpers.messages import INTERACTIVE_HELP, INTERACTIVE_SHORTCUTS
from onvif.cli.utils import (
    colorize,
    format_capabilities_as_services,
    format_services_list,
)
from onvif.utils.exceptions import ONVIFOperationException

from .context import ShellContext


class InformationCommands:
    """Provide information commands."""

    context: ShellContext
    _handle_connection_error: Callable[..., None]

    def do_help(self, arg):
        """Show help information."""
        if arg:
            cmd.Cmd.do_help(self, arg)
        else:
            print(INTERACTIVE_HELP)

    def do_shortcuts(self, _line) -> None:
        """Show available shortcuts."""
        print(INTERACTIVE_SHORTCUTS)

    def do_info(self, _line) -> None:
        """Show connection and device information."""
        # Build connection and CLI options info
        options_info = []

        # Connection options
        if hasattr(self.context.args, "https") and self.context.args.https:
            options_info.append(f"  Use HTTPS     : {colorize('True', 'green')}")

        if (
            hasattr(self.context.args, "no_verify_ssl")
            and self.context.args.no_verify_ssl
        ):
            options_info.append(f"  Verify SSL    : {colorize('False', 'red')}")

        if (
            hasattr(self.context.args, "timeout") and self.context.args.timeout != 10
        ):  # 10 is default
            options_info.append(
                f"  Timeout       : {colorize(f'{self.context.args.timeout}s', 'yellow')}"
            )

        # CLI options
        if hasattr(self.context.args, "debug") and self.context.args.debug:
            options_info.append(f"  Debug Mode    : {colorize('True', 'green')}")

        if hasattr(self.context.args, "no_patch") and self.context.args.no_patch:
            options_info.append(f"  ZeepPatcher   : {colorize('Disabled', 'red')}")

        if hasattr(self.context.args, "wsdl") and self.context.args.wsdl:
            options_info.append(
                f"  Custom WSDL   : {colorize(self.context.args.wsdl, 'yellow')}"
            )

        if (
            hasattr(self.context.args, "health_check_interval")
            and self.context.args.health_check_interval != 10
        ):  # 10 is default
            options_info.append(
                f"  Health Check  : every {colorize(f'{self.context.args.health_check_interval}s', 'yellow')}"
            )

        # Format options info
        options_display = ""
        if options_info:
            options_display = "\n" + "\n".join(options_info)

        # Display connection and device information using stored data
        print(
            f"\n{colorize('[ONVIF Terminal Client]', 'yellow')}"
            f"\n  Connected to  : "
            f"{colorize(f'{self.context.args.host}:{self.context.args.port}', 'yellow')}"
            f"\n  Auth Method   : "
            f"{colorize('HTTP Digest' if self.context.args.digest else 'WS-UsernameToken', 'yellow')}"
            f"{options_display}{self.context.device_info_text}"
        )
        print()  # Extra newline for spacing

    def do_capabilities(self, _line) -> None:
        """Show device capabilities in service format."""
        try:
            if (
                hasattr(self.context.client, "capabilities")
                and self.context.client.capabilities
            ):
                result = self.context.client.capabilities
            else:
                result = self.context.client.devicemgmt().GetCapabilities(
                    Category="All"
                )

            self.context.stored_data["capabilities"] = result
            self.context.stored_metadata["capabilities"] = {
                "service": "devicemgmt",
                "method": "GetCapabilities",
            }

            # Use special formatting for capabilities
            output = format_capabilities_as_services(result)
            print(output)
        except ONVIFOperationException as e:
            if isinstance(e.original_exception, (RequestException, TransportError)):
                self._handle_connection_error()
            else:
                print(f"{colorize('Error:', 'red')} {e}")

    def do_caps(self, line) -> None:
        """Show device capabilities (alias for 'capabilities')"""
        return self.do_capabilities(line)

    def do_services(self, _line) -> None:
        """Show available ONVIF services in service format."""
        try:
            if (
                hasattr(self.context.client, "services")
                and self.context.client.services
            ):
                result = self.context.client.services
            else:
                result = self.context.client.devicemgmt().GetServices(
                    IncludeCapability=False
                )

            self.context.stored_data["services"] = result
            self.context.stored_metadata["services"] = {
                "service": "devicemgmt",
                "method": "GetServices",
            }

            # Use special formatting for services
            output = format_services_list(result)
            print(output)
        except ONVIFOperationException as e:
            if isinstance(e.original_exception, (RequestException, TransportError)):
                self._handle_connection_error()
            else:
                print(f"{colorize('Error:', 'red')} {e}")

    def do_debug(self, _line) -> None:
        """Show debug information."""
        if self.context.client.xml_plugin:
            if self.context.last_method and self.context.last_operation_timestamp:
                print(f"{colorize('Last Operation:', 'cyan')}")
                print(
                    f"  operation: {self.context.last_service_name}.{self.context.last_method}()"
                )
                print(
                    f"  timestamp: {self.context.last_operation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                )

            print(f"{colorize('Last SOAP Request:', 'cyan')}")
            print(self.context.client.xml_plugin.last_sent_xml or "None")
            print(f"\n{colorize('Last SOAP Response:', 'cyan')}")
            print(self.context.client.xml_plugin.last_received_xml or "None")
        else:
            print(f"{colorize('Debug mode not enabled', 'yellow')}")
            print(
                f"Start CLI with {colorize('--debug', 'white')} flag to enable XML capture"
            )
