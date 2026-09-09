"""ONVIF CLI interactive shell implementation."""

import cmd
import json
import os
import re
import shutil
import socket
import ssl
import sys
import textwrap
import threading
import traceback
from datetime import datetime
from typing import Any

from requests.exceptions import RequestException
from zeep.exceptions import Fault, TransportError

from onvif.cli.helpers import get_method_documentation, get_operation_type_info
from onvif.cli.helpers.messages import (
    INTERACTIVE_HELP,
    INTERACTIVE_SHORTCUTS,
    print_interactive_intro,
)
from onvif.cli.utils import (
    colorize,
    format_capabilities_as_services,
    format_services_list,
    get_device_available_services,
    get_service_methods,
    get_service_required_args,
    parse_json_params,
)
from onvif.client import ONVIFClient
from onvif.utils.exceptions import ONVIFOperationException


class InteractiveShell(cmd.Cmd):
    """Interactive ONVIF CLI shell."""

    def __init__(self, client: ONVIFClient, args):
        super().__init__()
        self.client = client
        self.args = args
        self.current_service = None
        self.current_service_name = None
        self.stored_data: dict[str, Any] = {}  # For storing command results
        self.stored_metadata: dict[str, dict[str, Any]] = (
            {}
        )  # For storing metadata about stored data (service, method)
        self._last_result = None
        self._last_method = None
        self._last_service_name = None
        self._last_operation_timestamp = None

        # Define base commands
        self.base_commands = [
            "capabilities",
            "caps",
            "services",
            "help",
            "exit",
            "store",
            "rm",
            "show",
            "cls",
            "clear",
            "info",
            "debug",
            "ls",
            "cd",
            "pwd",
            "shortcuts",
            "desc",
            "type",
        ]

        # For background health check
        self._stop_health_check = threading.Event()
        self._health_check_thread = threading.Thread(
            target=self._periodic_health_check, daemon=True
        )

        # Enable tab completion
        try:
            import readline

            # Set completer to this instance
            readline.set_completer(self.complete)
            readline.set_completer_delims(" \t\n`!@#$%^&*()=+[{]}\\|;:'\",<>?")

            # Enable tab completion, making it compatible with both GNU readline and libedit
            if (
                hasattr(readline, "__doc__")
                and readline.__doc__
                and "libedit" in readline.__doc__
            ):
                readline.parse_and_bind("bind ^I rl_complete")
            else:
                readline.parse_and_bind("tab: complete")
        except ImportError:
            pass  # readline not available on some systems

        # Set prompt
        self.update_prompt()

        manufacturer = "Unknown"
        model = "Unknown"
        firmware = "Unknown"
        serial = "Unknown"
        hardware_id = "Unknown"
        onvif_version = "Unknown"

        try:
            # Get device information and store it
            self.device_data = self.client.devicemgmt().GetDeviceInformation()
            manufacturer = getattr(self.device_data, "Manufacturer", "Unknown")
            model = getattr(self.device_data, "Model", "Unknown")
            firmware = getattr(self.device_data, "FirmwareVersion", "Unknown")
            serial = getattr(self.device_data, "SerialNumber", "Unknown")
            hardware_id = getattr(self.device_data, "HardwareId", "Unknown")

            # Get ONVIF version
            services = self.client.devicemgmt().GetServices(IncludeCapability=False)
            devicemgmt_service = next(
                (
                    s
                    for s in services
                    if hasattr(s, "Namespace")
                    and s.Namespace == "http://www.onvif.org/ver10/device/wsdl"
                ),
                None,
            )
            if devicemgmt_service and hasattr(devicemgmt_service, "Version"):
                version = devicemgmt_service.Version
                major = getattr(version, "Major", "")
                minor = getattr(version, "Minor", "")
                if major and minor:
                    onvif_version = f"{major}.{minor}"
                elif major:
                    onvif_version = str(major)
        except ONVIFOperationException as e:
            if isinstance(e.original_exception, (RequestException, TransportError)):
                self._handle_connection_error(e)
            else:
                # For other errors (e.g., GetServices not supported), we can still proceed
                # with basic device info if GetDeviceInformation succeeded.
                pass

        self.device_info_text = (
            f"\n\n{colorize('[Device Info]', 'cyan')}\n"
            f"  Manufacturer  : {colorize(manufacturer, 'white')}\n"
            f"  Model         : {colorize(model, 'white')}\n"
            f"  Firmware      : {colorize(firmware, 'white')}\n"
            f"  Serial        : {colorize(serial, 'white')}\n"
            f"  HardwareId    : {colorize(hardware_id, 'white')}\n"
            f"  ONVIF Version : {colorize(onvif_version, 'white')}"
        )

        self.intro = print_interactive_intro(args, self.device_info_text)

        # Start background health check after successful initialization
        self._health_check_thread.start()

    def _periodic_health_check(self):
        """Periodically checks device connection using TCP or TLS depending on mode."""
        # Get health check interval from args, default to 10 seconds
        health_check_interval = getattr(self.args, "health_check_interval", 10)

        # Wait before first check to allow intro to finish
        self._stop_health_check.wait(health_check_interval)

        while not self._stop_health_check.is_set():
            sock = None
            try:
                # For HTTPS, use ssl.create_connection for proper TLS handling
                if getattr(self.args, "https", False):
                    context = ssl.create_default_context()
                    context.minimum_version = ssl.TLSVersion.TLSv1_2
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE

                    # Use ssl.create_connection instead of wrapping existing socket
                    sock = context.wrap_socket(
                        socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                        server_hostname=self.args.host,
                    )
                    sock.settimeout(5.0)
                    sock.connect((self.args.host, self.args.port))
                else:
                    # For HTTP, simple TCP connection check
                    sock = socket.create_connection(
                        (self.args.host, self.args.port), timeout=5.0
                    )

                # Connection successful
            except (
                socket.timeout,
                ConnectionRefusedError,
                socket.gaierror,
                ssl.SSLError,
                ssl.SSLEOFError,
                OSError,
            ) as e:
                # Connection failed, trigger exit
                print(
                    f"\n{colorize('Connection to device lost.', 'red')}",
                    file=sys.stderr,
                )
                print(
                    f"{colorize('Error:', 'red')} Health check failed: {e}",
                    file=sys.stderr,
                )
                print(
                    colorize("Exiting ONVIF interactive shell...", "yellow"),
                    file=sys.stderr,
                )
                # Forcibly exit the entire process. This is necessary to interrupt
                # the blocking input() call in the main thread.
                os._exit(1)
            finally:
                # Ensure the socket is always closed
                if sock:
                    sock.close()

            # Wait before next check or stop signal
            self._stop_health_check.wait(health_check_interval)

    def _handle_connection_error(self, e):  # pylint: disable=unused-argument
        """Handle connection errors by notifying the user and exiting."""
        print(f"\n{colorize('Connection to device lost.', 'red')}", file=sys.stderr)
        # print(f"{colorize('Error:', 'red')} {e}", file=sys.stderr)
        if self.args.debug:
            traceback.print_exc()
        print(colorize("Exiting ONVIF interactive shell...", "yellow"), file=sys.stderr)
        print(colorize("Goodbye!", "cyan"), file=sys.stderr)
        sys.exit(1)

    def _split_multi_commands(self, s: str) -> list:
        """Split a command string by top-level '&&' separators while ignoring
        occurrences inside quotes or bracketed structures.

        Returns a list of command strings (trimmed).
        """
        parts = []
        buf = []
        i = 0
        length = len(s)
        depth = 0
        in_single = False
        in_double = False
        while i < length:
            ch = s[i]
            # Toggle quote states
            if ch == "'" and not in_double:
                in_single = not in_single
                buf.append(ch)
                i += 1
                continue
            if ch == '"' and not in_single:
                in_double = not in_double
                buf.append(ch)
                i += 1
                continue

            # Track bracket depth to avoid splitting inside {...} or [...]
            if not in_single and not in_double:
                if ch in "{[(":
                    depth += 1
                elif ch in "}])":
                    depth = max(0, depth - 1)

            # Detect top-level &&
            if (
                not in_single
                and not in_double
                and depth == 0
                and ch == "&"
                and i + 1 < length
                and s[i + 1] == "&"
            ):
                # finish current buffer
                token = "".join(buf).strip()
                parts.append(token)
                buf = []
                i += 2
                # skip optional spaces after &&
                while i < length and s[i].isspace():
                    i += 1
                continue

            buf.append(ch)
            i += 1

        if buf:
            token = "".join(buf).strip()
            if token:
                parts.append(token)

        return parts

    def _display_grid(self, items):
        """Display items in grid format matching TAB completion (vertical layout)"""
        if not items:
            return

        # Get device services for coloring (only in root mode)
        services = (
            get_device_available_services(self.client)
            if not self.current_service
            else []
        )

        # Calculate terminal width
        try:
            term_width = shutil.get_terminal_size().columns
        except (KeyError, ValueError, RuntimeError):
            term_width = 80

        # Find the longest item length
        longest_length = max(len(item) for item in items)

        # Column width calculation: use same algorithm as cmd.Cmd.columnize()
        # Python's columnize uses: maxlen + 2 if maxlen > 0 else 2
        col_width = longest_length + 2 if longest_length > 0 else 2

        # Calculate number of columns that fit
        num_cols = max(1, term_width // col_width)

        # Calculate number of rows needed
        num_rows = (len(items) + num_cols - 1) // num_cols

        # Display items in VERTICAL layout (column by column, like TAB completion)
        for row_idx in range(num_rows):
            row_items = []
            for col_idx in range(num_cols):
                # Calculate index in vertical order
                item_idx = col_idx * num_rows + row_idx

                if item_idx < len(items):
                    item = items[item_idx]

                    # Apply coloring
                    if item in services:
                        colored_item = colorize(item, "cyan")
                    else:
                        colored_item = item

                    # Calculate padding: align to column width
                    # Use ljust-style padding for consistency with cmd.Cmd
                    padding = col_width - len(item)
                    formatted_item = colored_item + " " * padding
                    row_items.append(formatted_item)

            if row_items:
                # Join and rstrip to remove trailing spaces
                line = "".join(row_items).rstrip()
                print(line)

    def _resolve_stored_reference(self, reference: str):
        """Resolve stored data reference like 'profiles[0].token' or 'profiles.Token'.

        Args:
            reference: String reference like 'profiles[0]' or 'profiles.Token'

        Returns:
            Resolved value or None if not found
        """
        # Parse the reference - e.g., "profiles[0].token" or "services.Namespace"
        # Split by dots and brackets
        parts = re.split(r"\.|\[|\]", reference)
        parts = [p for p in parts if p]  # Remove empty strings

        if not parts:
            return None

        # Start with the stored variable name
        var_name = parts[0]
        if var_name not in self.stored_data:
            return None

        current = self.stored_data[var_name]

        # Navigate through the rest of the path
        for part in parts[1:]:
            try:
                # Check if it's an integer index
                if part.isdigit():
                    index = int(part)
                    if isinstance(current, (list, tuple)):
                        current = current[index]
                    else:
                        # Try to convert to list if it's iterable
                        try:
                            current = list(current)[index]
                        except (TypeError, IndexError):
                            return None
                else:
                    # It's an attribute name
                    if hasattr(current, part):
                        current = getattr(current, part)
                    elif isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return None
            except (IndexError, AttributeError, KeyError, TypeError):
                return None

        return current

    def _substitute_stored_references(self, params_str: str) -> str:
        """Substitute $variable references in parameter string with stored data.

        Args:
            params_str: Parameter string that may contain $variable references

        Returns:
            Parameter string with substituted values
        """
        # Find all $variable references (e.g., $profiles[0].token)
        pattern = (
            r"\$([a-zA-Z_][a-zA-Z0-9_]*(?:\[[0-9]+\])?(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)"
        )

        def replace_reference(match):
            reference = match.group(1)
            value = self._resolve_stored_reference(reference)

            if value is None:
                print(f"{colorize('Warning:', 'yellow')} Cannot resolve ${reference}")
                return match.group(0)  # Keep original if not found

            # Convert value to string representation suitable for JSON
            # Use json.dumps to serialize values correctly for JSON parsing.
            # This preserves numbers, booleans, nulls, arrays and objects.
            try:
                return json.dumps(value)
            except (KeyError, ValueError, RuntimeError):
                # Fall back to string-quoting for anything not serializable
                return json.dumps(str(value))

        return re.sub(pattern, replace_reference, params_str)

    def update_prompt(self):
        """Update command prompt based on current context."""
        if self.current_service_name:
            self.prompt = f"{self.args.username}@{self.args.host}:{self.args.port}/{self.current_service_name} > "
        else:
            self.prompt = f"{self.args.username}@{self.args.host}:{self.args.port} > "

    def onecmd(self, line):
        """Override onecmd to handle service method calls without showing cmd.Cmd
        traceback."""
        line = line.strip()
        if not line:
            return self.emptyline()

        # Support chaining multiple commands with && (only at top-level,
        # not inside quotes/brackets). Example:
        #   media && GetProfiles && store profiles
        if "&&" in line:
            parts = self._split_multi_commands(line)
            stop = None
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                stop = self.onecmd(part)
                if stop:
                    return stop
            return None

        # Check if we're in service mode and this might be a method call
        if self.current_service and line and not line.startswith("do_"):
            # Check if it's a known command first
            command, _, line = self.parseline(line)
            if command and hasattr(self, f"do_{command}"):
                # It's a known command, let parent handle it normally
                return super().onecmd(line)

            # It might be a service method call, handle it directly
            return self.default(line)

        # For all other cases, use normal cmd.Cmd processing
        return super().onecmd(line)

    def default(self, line):
        """Handle unknown commands."""
        available_services = get_device_available_services(self.client)

        # Check if it's a service call (with or without arguments)
        # Extract first word to check if it's a service name
        first_word = line.split()[0] if line.split() else line

        if first_word in available_services:
            return self.do_enter_service(line)

        # Check if the whole line (without arguments) is a service
        if line in available_services:
            return self.do_enter_service(line)

        # Check if it's a method call in service context
        if self.current_service:
            if self.current_service and " " in line:
                parts = line.split(" ", 1)
                method_name = parts[0]
                params_str = parts[1] if len(parts) > 1 else ""
                return self.execute_service_method(method_name, params_str)

            # Method without parameters
            return self.execute_service_method(line, "")

        # Try to find suggestions for partial commands
        suggestions = self.get_suggestions(line)
        if suggestions:
            print(f"{colorize('Unknown command:', 'red')} {line}")
            print(f"{colorize('Did you mean:', 'yellow')} {', '.join(suggestions)}")
        else:
            print(f"{colorize('Unknown command:', 'red')} {line}")
            print(f"Type {colorize('help', 'white')} for available commands")

    def get_suggestions(self, partial_cmd: str) -> list[str]:
        """Get command suggestions based on partial input."""
        suggestions = []

        if self.current_service:
            # In service mode - suggest methods
            methods = get_service_methods(self.current_service)
            # Add helper commands in service mode
            methods.extend([colorize("type", "yellow"), colorize("desc", "yellow")])
            for method in methods:
                if method.lower().startswith(partial_cmd.lower()):
                    suggestions.append(method)
        else:
            # In root mode - suggest device-specific services and commands
            services = get_device_available_services(
                self.client
            )  # Use device-specific services
            commands = self.base_commands

            for service in services:
                if service.lower().startswith(partial_cmd.lower()):
                    suggestions.append(colorize(service, "cyan"))

            for cmd_base in commands:
                if cmd_base.lower().startswith(partial_cmd.lower()):
                    suggestions.append(cmd_base)

        return suggestions[:5]  # Limit to 5 suggestions

    def completenames(self, text: str, *ignored) -> list[str]:
        """Tab completion for command names."""
        if self.current_service:
            # Complete method names in service mode
            methods = get_service_methods(self.current_service)
            # Add helper commands in service mode
            methods.extend([colorize("type", "yellow"), colorize("desc", "yellow")])
            completions = [
                method for method in methods if method.lower().startswith(text.lower())
            ]
        else:
            # Complete device-specific service names and basic commands in root mode
            services = get_device_available_services(
                self.client
            )  # Use device-specific services
            commands = self.base_commands
            all_completions = services + commands
            completions = [
                cmd for cmd in all_completions if cmd.lower().startswith(text.lower())
            ]

        return completions

    def cmdloop(self, intro=None):
        """Override cmdloop to handle TAB completion manually."""
        if intro is not None:
            self.intro = intro
        if self.intro:
            self.stdout.write(str(self.intro) + "\n")

        stop = None
        while not stop:
            if self.cmdqueue:
                line = self.cmdqueue.pop(0)
            else:
                try:
                    line = input(self.prompt)
                except EOFError:
                    line = "EOF"
                except KeyboardInterrupt:
                    print("^C")
                    line = ""

            line = self.precmd(line)
            stop = self.onecmd(line)
            stop = self.postcmd(stop, line)

    def columnize(self, list, displaywidth=80):  # pylint: disable=redefined-builtin
        """Override columnize to use grid format for TAB completion."""
        if not list:
            return

        # Use our grid display for TAB completion with coloring enabled
        self._display_grid(list)

    def print_topics(self, header, cmds, cmdlen, maxcol):
        """Override print_topics to use grid format for TAB completion."""
        if not cmds:
            return

        # Print without header if it's empty or whitespace
        if header.strip():
            self.stdout.write(f"{header}\n")

        # Use our grid display for TAB completion with coloring enabled
        self._display_grid(cmds)

    def do_capabilities(self, line):  # pylint: disable=unused-argument
        """Show device capabilities in service format."""
        try:
            if hasattr(self.client, "capabilities") and self.client.capabilities:
                result = self.client.capabilities
            else:
                result = self.client.devicemgmt().GetCapabilities(Category="All")

            self.stored_data["capabilities"] = result
            self.stored_metadata["capabilities"] = {
                "service": "devicemgmt",
                "method": "GetCapabilities",
            }

            # Use special formatting for capabilities
            output = format_capabilities_as_services(result)
            print(output)
        except ONVIFOperationException as e:
            if isinstance(e.original_exception, (RequestException, TransportError)):
                self._handle_connection_error(e)
            else:
                print(f"{colorize('Error:', 'red')} {e}")

    def do_services(self, line):  # pylint: disable=unused-argument
        """Show available services in service format."""
        try:
            if hasattr(self.client, "services") and self.client.services:
                result = self.client.services
            else:
                result = self.client.devicemgmt().GetServices(IncludeCapability=False)

            self.stored_data["services"] = result
            self.stored_metadata["services"] = {
                "service": "devicemgmt",
                "method": "GetServices",
            }

            # Use special formatting for services
            output = format_services_list(result)
            print(output)
        except ONVIFOperationException as e:
            if isinstance(e.original_exception, (RequestException, TransportError)):
                self._handle_connection_error(e)
            else:
                print(f"{colorize('Error:', 'red')} {e}")

    def do_enter_service(self, line):
        """Enter service mode with optional arguments for services that require them."""
        # Parse service name and arguments
        parts = line.split(None, 1)
        service_name = parts[0] if parts else ""
        args_str = parts[1] if len(parts) > 1 else ""

        available_services = get_device_available_services(self.client)
        if service_name not in available_services:
            print(f"{colorize('Error:', 'red')} Unknown service '{service_name}'")
            colored_services = [colorize(svc, "cyan") for svc in available_services]
            print(f"Available services: {', '.join(colored_services)}")
            return

        try:
            # Check if this service requires arguments
            required_args = get_service_required_args(service_name)

            if required_args:
                # Service requires arguments
                if not args_str:
                    # No arguments provided, show help
                    print(
                        f"{colorize('Error:', 'red')} Service '{service_name}' requires arguments"
                    )
                    print(
                        f"{colorize('Usage:', 'yellow')} {service_name} {' '.join([f'{arg}=<value>' for arg in required_args])}"
                    )
                    print(
                        f"{colorize('Example:', 'yellow')} {service_name} {required_args[0]}=$subscription"
                    )
                    return

                # Parse arguments
                try:
                    parsed_args = parse_json_params(args_str)
                except (OSError, AttributeError, ValueError, TypeError) as e:
                    print(f"{colorize('Error parsing arguments:', 'red')} {e}")
                    return

                # Check if all required arguments are provided
                missing_args = [arg for arg in required_args if arg not in parsed_args]
                if missing_args:
                    print(
                        f"{colorize('Error:', 'red')} Missing required arguments: {', '.join(missing_args)}"
                    )
                    print(
                        f"{colorize('Usage:', 'yellow')} {service_name} {' '.join([f'{arg}=<value>' for arg in required_args])}"
                    )
                    return

                # Resolve stored references in arguments
                for arg_name in required_args:
                    arg_value = parsed_args[arg_name]
                    if isinstance(arg_value, str) and arg_value.startswith("$"):
                        # Resolve stored reference
                        reference = arg_value[1:]  # Remove $ prefix
                        resolved_value = self._resolve_stored_reference(reference)
                        if resolved_value is None:
                            print(
                                f"{colorize('Error:', 'red')} Could not resolve reference '{arg_value}'"
                            )
                            return
                        parsed_args[arg_name] = resolved_value

                # Call service method with arguments
                service_method = getattr(self.client, service_name)
                service = service_method(**parsed_args)
            else:
                # Service doesn't require arguments
                service = getattr(self.client, service_name)()

            self.current_service = service
            self.current_service_name = service_name
            self.update_prompt()

            print(
                f"{colorize('Entered service:', 'yellow')} {colorize(service_name, 'cyan')}"
            )

            # Show available methods
            methods = get_service_methods(service)
            methods_preview = ", ".join(methods[:10])
            if len(methods) > 10:
                print(
                    f"{colorize('Available methods:', 'yellow')} {methods_preview} ... and {colorize(f'{len(methods) - 10} more.', 'yellow')}"
                )
                print(
                    f"Type {colorize('ls', 'cyan')}/press <{colorize('TAB', 'yellow')}> to see all."
                )
            else:
                print(f"{colorize('Available methods:', 'yellow')} {methods_preview}")
            print(f"Type {colorize('up', 'cyan')} to exit service mode.")

        except (OSError, RuntimeError, ValueError, AttributeError) as e:
            print(f"{colorize('Error entering service:', 'red')} {e}")
            if self.args.debug:
                traceback.print_exc()

    def do_ls(self, line):  # pylint: disable=unused-argument
        """List available commands/services like TAB completion."""
        if self.current_service:
            # In service mode - show available methods
            methods = get_service_methods(self.current_service)
            # Add helper commands in service mode
            methods.extend([colorize("type", "yellow"), colorize("desc", "yellow")])
            if methods:
                # Use the same display format as TAB completion
                self._display_grid(methods)
            else:
                print("No methods available")
        else:
            # In root mode - show device-specific services and commands
            services = get_device_available_services(self.client)
            commands = self.base_commands
            all_items = services + commands

            if all_items:
                # Use the same display format as TAB completion
                self._display_grid(all_items)
            else:
                print("No commands available")

    def do_desc(self, line):
        """Describes a method from its WSDL documentation.

        Usage: desc <method_name>
        """
        method_name = line.strip()

        if not self.current_service:
            print(
                f"{colorize('Error:', 'red')} You must be in a service mode to use 'desc'."
            )
            print(f"Enter a service first (e.g., {colorize('devicemgmt', 'yellow')})")
            return

        if not method_name:
            print("Usage: desc <method_name>")
            return

        if not hasattr(self.current_service, method_name):
            print(
                f"{colorize('Error:', 'red')} Method '{method_name}' not found in service '{self.current_service_name}'."
            )
            print(f"Use {colorize('ls', 'yellow')} to see available methods.")
            return

        doc_info = get_method_documentation(self.current_service, method_name)

        if doc_info:
            print(
                f"\n{colorize('Description for', 'yellow')} {self.current_service_name}.{method_name}():"
            )
            doc_parts = doc_info["doc"].split("\n")
            for part in doc_parts:
                wrapped_doc = textwrap.fill(
                    part, width=100, initial_indent="  ", subsequent_indent="  "
                )
                print(colorize(wrapped_doc, "white"))

            if doc_info["required"]:
                print(f"\n{colorize('Required Arguments:', 'green')}")
                for arg in doc_info["required"]:
                    print(f"  - {arg}")

            if doc_info["optional"]:
                print(f"\n{colorize('Optional Arguments:', 'cyan')}")
                for arg in doc_info["optional"]:
                    print(f"  - {arg}")
            print()  # Add a newline for better spacing
        else:
            print(
                f"No documentation or parameter info found for method '{method_name}'."
            )

    def complete_desc(
        self, text, line, begidx, endidx
    ):  # pylint: disable=unused-argument
        """Autocomplete method names for desc command."""
        if not self.current_service:
            return []
        methods = get_service_methods(self.current_service)
        return [m for m in methods if m.lower().startswith(text.lower())]

    def do_type(self, line):
        """Show input and output types for a method.

        Usage: type <method_name>
        """
        method_name = line.strip()

        if not self.current_service:
            print(
                f"{colorize('Error:', 'red')} You must be in a service mode to use 'type'."
            )
            print(f"Enter a service first (e.g., {colorize('devicemgmt', 'yellow')})")
            return

        if not method_name:
            print("Usage: type <method_name>")
            return

        if not hasattr(self.current_service, method_name):
            print(
                f"{colorize('Error:', 'red')} Method '{method_name}' not found in service '{self.current_service_name}'."
            )
            print(f"Use {colorize('ls', 'yellow')} to see available methods.")
            return

        type_info = get_operation_type_info(self.current_service, method_name)

        if type_info:
            # Helper function to display parameters recursively with tree-style indentation
            def display_params(params, prefix_lines=None, is_root_level=False):
                """Display parameters with tree-style formatting.

                Args:
                    params: List of parameter dictionaries
                    prefix_lines: List of strings representing the tree prefix for each line
                    is_root_level: If True, don't show tree characters at this level
                """
                if prefix_lines is None:
                    prefix_lines = []

                for idx, param in enumerate(params):
                    is_last = idx == len(params) - 1

                    # Determine tree characters (only if not root level)
                    if is_root_level:
                        tree_branch = ""
                        tree_continue = ""
                    else:
                        if is_last:
                            tree_branch = "└── "
                            tree_continue = "    "
                        else:
                            tree_branch = "├── "
                            tree_continue = "│   "

                    # Determine prefix symbol: + for attributes, - for elements
                    prefix_symbol = "+" if param.get("is_attribute", False) else "-"

                    # Format occurrences based on type
                    occurs = ""
                    if param.get("is_attribute", False):
                        # For attributes: only show "required" if use="required"
                        # Default for attributes is optional (no label needed)
                        if param["minOccurs"] == "1":  # This means use="required"
                            occurs = f" - {colorize('required', 'yellow')}"
                        # If minOccurs == "0", it's optional (default), so no label
                    else:
                        # For elements: show unbounded, optional, or required
                        if param["maxOccurs"] == "unbounded":
                            occurs = f" - {colorize('unbounded', 'magenta')}"
                        elif param["minOccurs"] == "0":
                            occurs = f" - {colorize('optional', 'green')}"
                        else:
                            occurs = f" - {colorize('required', 'yellow')}"

                    # Format type
                    type_str = f"[{param['type']}]" if param["type"] else ""

                    # Build the current line prefix from all previous levels
                    current_prefix = "".join(prefix_lines)

                    # Add spacing for root level items
                    if is_root_level:
                        current_prefix = "  "

                    # Display parameter name with tree structure, prefix, occurrence, and type
                    # Only add semicolon separator if there's an occurrence label
                    separator = ";" if occurs else ""
                    param_line = (
                        f"{current_prefix}{tree_branch}{prefix_symbol}{colorize(param['name'], 'white')}"
                        f"{occurs}{separator} {colorize(type_str, 'cyan')}"
                    )
                    print(param_line)

                    # Display documentation if available
                    if param.get("documentation"):
                        doc_lines = param["documentation"].split("\n")
                        for doc_line in doc_lines:
                            if doc_line.strip():
                                # Add tree continuation for documentation
                                if is_root_level:
                                    doc_prefix = "  "
                                else:
                                    doc_prefix = current_prefix + tree_continue
                                wrapped_doc = textwrap.fill(
                                    doc_line.strip(),
                                    width=96,  # Slightly less to account for tree chars
                                    initial_indent=doc_prefix + "  ",
                                    subsequent_indent=doc_prefix + "  ",
                                )
                                print(colorize(wrapped_doc, "reset"))

                    # Display children recursively with updated prefix
                    if param.get("children"):
                        if is_root_level:
                            # Start tree structure from children
                            new_prefix_lines = ["  "]
                        else:
                            new_prefix_lines = prefix_lines + [tree_continue]
                        display_params(
                            param["children"], new_prefix_lines, is_root_level=False
                        )

            input_msg = type_info["input"]
            # Display Input
            if input_msg is not None:
                print(f"\n{colorize('Input:', 'cyan')}")
                msg_name = f"[{input_msg['name']}]"
                print(f"{colorize(msg_name, 'yellow')}")

                if input_msg["parameters"]:
                    display_params(input_msg["parameters"], is_root_level=True)
                else:
                    print(f"  {colorize('(no parameters)', 'reset')}")
            else:
                print(
                    f"\n{colorize('Input:', 'cyan')} {colorize('(not defined)', 'reset')}"
                )

            output_msg = type_info["output"]
            # Display Output
            if output_msg is not None:
                print(f"\n{colorize('Output:', 'cyan')}")
                msg_name = f"[{output_msg['name']}]"
                print(f"{colorize(msg_name, 'yellow')}")

                if output_msg["parameters"]:
                    display_params(output_msg["parameters"], is_root_level=True)
                else:
                    print(f"  {colorize('(no parameters)', 'reset')}")
            else:
                print(
                    f"\n{colorize('Output:', 'cyan')} {colorize('(not defined)', 'reset')}"
                )

            print()  # Add newline for spacing
        else:
            print(
                f"{colorize('Error:', 'red')} Could not retrieve type information for '{method_name}'."
            )

    def complete_type(
        self, text, line, begidx, endidx
    ):  # pylint: disable=unused-argument
        """Autocomplete method names for type command."""
        if not self.current_service:
            return []
        methods = get_service_methods(self.current_service)
        return [m for m in methods if m.lower().startswith(text.lower())]

    def do_cd(self, line):
        """Change to service directory (alias for entering service)"""
        if not line:
            print("Usage: cd <service_name>")
            available_services = get_device_available_services(self.client)
            colored_services = [colorize(svc, "cyan") for svc in available_services]
            print(f"Available services: {', '.join(colored_services)}")
            return
        return self.do_enter_service(line)

    def complete_cd(
        self, text, line, begidx, endidx
    ):  # pylint: disable=unused-argument
        """Autocomplete service names for cd command."""
        services = get_device_available_services(self.client)
        return [s for s in services if s.lower().startswith(text.lower())]

    def do_pwd(self, line):  # pylint: disable=unused-argument
        """Show current service context."""
        if self.current_service_name:
            print(
                f"{colorize('Current service:', 'yellow')} {colorize(self.current_service_name, 'cyan')}"
            )
        else:
            print(
                f"{colorize('Current context:', 'yellow')} {colorize('root', 'blue')}"
            )

    def do_shortcuts(self, line):  # pylint: disable=unused-argument
        """Show available shortcuts."""
        print(INTERACTIVE_SHORTCUTS)

    def do_caps(self, line):
        """Show device capabilities (alias for 'capabilities')"""
        return self.do_capabilities(line)

    def do_up(self, line):  # pylint: disable=unused-argument
        """Exit current service mode (go up one level)"""
        if self.current_service:
            print(
                f"{colorize('Exited service:', 'yellow')} {colorize(f'{self.current_service_name}', 'cyan')}"
            )
            self.current_service = None
            self.current_service_name = None
            self.update_prompt()
        else:
            print("Not in service mode")

    def do_exit_service(self, line):
        """Exit current service mode (alias for 'up')"""
        return self.do_up(line)

    def do_store(self, line):
        """Store last result with a name: store <name>"""
        if not line:
            print("Usage: store <name>")
            return
        # Only allow valid Python variable names
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", line):
            print(
                f"{colorize('Error:', 'red')} Invalid name '{line}'. "
                "Only letters, numbers, and underscores allowed, and must not start with a number."
            )
            return
        # Must be unique
        if line in self.stored_data:
            print(
                f"{colorize('Error:', 'red')} Name '{line}' already exists. "
                "Use a different name or remove it first."
            )
            return
        if hasattr(self, "_last_result"):
            self.stored_data[line] = self._last_result
            # Store metadata (service and method info)
            metadata = {}
            if self.current_service_name:
                metadata["service"] = self.current_service_name
            if hasattr(self, "_last_method"):
                metadata["method"] = self._last_method
            self.stored_metadata[line] = metadata
            service = metadata.get("service", "unknown")
            method = metadata.get("method", "unknown")
            print(
                f"{colorize('Stored result as:', 'green')} {colorize('$'+line, 'yellow')} - "
                f"{colorize(service, 'cyan')}.{colorize(method, 'white')}()"
            )
        else:
            print(f"{colorize('Error:', 'red')} No result to store")

    def do_rm(self, line):
        """Remove stored data: rm <name>"""
        if not line:
            print("Usage: rm <name>")
            return
        if line in self.stored_data:
            del self.stored_data[line]
            if line in self.stored_metadata:
                del self.stored_metadata[line]
            print(f"{colorize('Removed:', 'yellow')} {colorize('$'+line, 'cyan')}")
        else:
            print(f"{colorize('Error:', 'red')} No stored data named '{line}'")

    def complete_rm(
        self, text, line, begidx, endidx
    ):  # pylint: disable=unused-argument
        """Autocomplete stored variable names for rm command."""
        return [name for name in self.stored_data if name.startswith(text)]

    def do_show(self, line):
        """Show stored data: show <name> or show <name>.<attribute> or show
        <name>[index]"""
        if not line:
            print(colorize("Stored data:", "green"))
            for name in self.stored_data:
                # Get metadata if available
                metadata = self.stored_metadata.get(name, {})
                service = metadata.get("service", "unknown")
                method = metadata.get("method", "unknown")

                # Format: name - service.method()
                info = (
                    f"{colorize('$'+name, 'yellow')} - "
                    f"{colorize(service, 'cyan')}.{colorize(method, 'white')}()"
                )
                print(f"  {info}")
            return

        # Parse accessor expression (e.g., profiles[0].token or profiles.Token)
        result = self._resolve_stored_reference(line)
        if result is not None:
            print(str(result))
        else:
            print(f"{colorize('Error:', 'red')} Cannot resolve '{line}'")

    def complete_show(
        self, text, line, begidx, endidx
    ):  # pylint: disable=unused-argument
        """Autocomplete stored variable names for show command."""
        # Get the part being completed
        parts = line.split()
        if len(parts) <= 1 or (len(parts) == 2 and not line.endswith(" ")):
            # Completing the variable name
            return [name for name in self.stored_data if name.startswith(text)]
        return []

    def do_clear(self, line):  # pylint: disable=unused-argument
        """Clear terminal screen."""
        # Clear screen for both Windows and Unix-like systems
        os.system("cls" if os.name == "nt" else "clear")

    def do_cls(self, line):  # pylint: disable=unused-argument
        """Clear stored data."""
        self.stored_data.clear()
        self.stored_metadata.clear()
        print(f"{colorize('Cleared all stored data', 'yellow')}")

    def do_info(self, line):  # pylint: disable=unused-argument
        """Show connection and device information."""
        # Build connection and CLI options info
        options_info = []

        # Connection options
        if hasattr(self.args, "https") and self.args.https:
            options_info.append(f"  Use HTTPS     : {colorize('True', 'green')}")

        if hasattr(self.args, "no_verify_ssl") and self.args.no_verify_ssl:
            options_info.append(f"  Verify SSL    : {colorize('False', 'red')}")

        if hasattr(self.args, "timeout") and self.args.timeout != 10:  # 10 is default
            options_info.append(
                f"  Timeout       : {colorize(f'{self.args.timeout}s', 'yellow')}"
            )

        # CLI options
        if hasattr(self.args, "debug") and self.args.debug:
            options_info.append(f"  Debug Mode    : {colorize('True', 'green')}")

        if hasattr(self.args, "no_patch") and self.args.no_patch:
            options_info.append(f"  ZeepPatcher   : {colorize('Disabled', 'red')}")

        if hasattr(self.args, "wsdl") and self.args.wsdl:
            options_info.append(
                f"  Custom WSDL   : {colorize(self.args.wsdl, 'yellow')}"
            )

        if (
            hasattr(self.args, "health_check_interval")
            and self.args.health_check_interval != 10
        ):  # 10 is default
            options_info.append(
                f"  Health Check  : every {colorize(f'{self.args.health_check_interval}s', 'yellow')}"
            )

        # Format options info
        options_display = ""
        if options_info:
            options_display = "\n" + "\n".join(options_info)

        # Display connection and device information using stored data
        print(
            f"\n{colorize('[ONVIF Terminal Client]', 'yellow')}"
            f"\n  Connected to  : {colorize(f'{self.args.host}:{self.args.port}', 'yellow')}"
            f"{options_display}{self.device_info_text}"
        )
        print()  # Extra newline for spacing

    def execute_service_method(self, method_name, params_str):
        """Execute a method on the current service."""
        if not self.current_service:
            print(f"{colorize('Error:', 'red')} Not in service mode")
            return

        try:
            method = getattr(self.current_service, method_name)
        except AttributeError:
            print(
                f"{colorize('Error:', 'red')} Unknown method '{method_name}' for service '{self.current_service_name}'"
            )
            available_methods = get_service_methods(self.current_service)
            print(
                f"{colorize('Available methods:', 'yellow')} {', '.join(available_methods[:5])}"
            )
            if len(available_methods) > 5:
                print(
                    f"Type {colorize('ls', 'cyan')}/press {colorize('<TAB>', 'yellow')} to see all available methods"
                )
            return

        try:
            # Substitute stored data references before parsing
            if params_str and "$" in params_str:
                params_str = self._substitute_stored_references(params_str)

            params = parse_json_params(params_str) if params_str else {}
            result = method(**params)

            self._last_result = result
            self._last_method = method_name  # Store method name for metadata
            self._last_service_name = self.current_service_name  # Store service name
            self._last_operation_timestamp = datetime.now()
            print(str(result))

        except (ONVIFOperationException, ValueError, TypeError) as e:
            # Check if it's a connection error (must be wrapped in ONVIFOperationException)
            if isinstance(e, ONVIFOperationException) and isinstance(
                e.original_exception, (RequestException, TransportError)
            ):
                self._handle_connection_error(e)
            else:
                # For all other errors (SOAP faults, TypeErrors, etc.), just print and continue.
                print(f"{colorize('Error:', 'red')} {e}")
                if self.args.debug:
                    # In debug mode, show traceback for unexpected errors, but not for
                    # common user errors like SOAP faults or missing arguments (TypeError).
                    is_soap_fault = isinstance(
                        e, ONVIFOperationException
                    ) and isinstance(e.original_exception, Fault)
                    if not is_soap_fault and not isinstance(e, TypeError):
                        traceback.print_exc()

    def do_debug(self, line):  # pylint: disable=unused-argument
        """Show debug information."""
        if self.client.xml_plugin:
            if self._last_method and self._last_operation_timestamp:
                print(f"{colorize('Last Operation:', 'cyan')}")
                print(f"  operation: {self._last_service_name}.{self._last_method}()")
                print(
                    f"  timestamp: {self._last_operation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                )

            print(f"{colorize('Last SOAP Request:', 'cyan')}")
            print(self.client.xml_plugin.last_sent_xml or "None")
            print(f"\n{colorize('Last SOAP Response:', 'cyan')}")
            print(self.client.xml_plugin.last_received_xml or "None")
        else:
            print(f"{colorize('Debug mode not enabled', 'yellow')}")
            print(
                f"Start CLI with {colorize('--debug', 'white')} flag to enable XML capture"
            )

    def do_exit(self, line):  # pylint: disable=unused-argument
        """Exit the shell."""
        self._stop_health_check.set()
        print(colorize("Goodbye!", "cyan"))
        return True

    def emptyline(self):
        """Handle empty line."""

    def do_help(self, arg):
        """Show help information."""
        if arg:
            super().do_help(arg)
        else:
            print(INTERACTIVE_HELP)

    def run(self):
        """Run the interactive shell."""
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print(f"\n{colorize('Goodbye!', 'cyan')}")
            self._stop_health_check.set()
            sys.exit(0)
