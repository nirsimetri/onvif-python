"""Navigation commands implementation."""

from __future__ import annotations

import traceback
from typing import Any, Callable

from onvif.cli.utils import (
    colorize,
    get_device_available_services,
    get_service_methods,
    get_service_required_args,
    parse_json_params,
)

from .context import ShellContext


class NavigationCommands:
    """Provide navigation commands."""

    context: ShellContext
    _display_grid: Callable[..., None]
    _resolve_stored_reference: Callable[[str], Any | None]
    update_prompt: Callable[[], None]

    def do_ls(self, _line) -> None:
        """List available commands/services like TAB completion."""
        if self.context.current_service:
            # In service mode - show available methods
            methods = get_service_methods(self.context.current_service)
            # Add helper commands in service mode
            methods.extend([colorize("type", "yellow"), colorize("desc", "yellow")])
            if methods:
                # Use the same display format as TAB completion
                self._display_grid(methods)
            else:
                print("No methods available")
        else:
            # In root mode - show device-specific services and commands
            services = get_device_available_services(self.context.client)
            commands = self.context.base_commands
            all_items = services + commands

            if all_items:
                # Use the same display format as TAB completion
                self._display_grid(all_items)
            else:
                print("No commands available")

    def do_cd(self, line) -> None:
        """Change to service directory (alias for entering service)"""
        if not line:
            print("Usage: cd <service_name>")
            available_services = get_device_available_services(self.context.client)
            colored_services = [colorize(svc, "cyan") for svc in available_services]
            print(f"Available services: {', '.join(colored_services)}")
            return None
        return self.do_enter_service(line)

    def complete_cd(self, text, _line, _begidx, _endidx) -> list:
        """Autocomplete service names for cd command."""
        services = get_device_available_services(self.context.client)
        return [s for s in services if s.lower().startswith(text.lower())]

    def do_up(self, _line) -> None:
        """Exit current service mode (go up one level)"""
        if self.context.current_service:
            print(
                f"{colorize('Exited service:', 'yellow')} "
                f"{colorize(f'{self.context.current_service_name}', 'cyan')}"
            )
            self.context.current_service = None
            self.context.current_service_name = None
            self.update_prompt()
        else:
            print("Not in service mode")

    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    def do_enter_service(self, line) -> None:
        """Enter service mode with optional arguments for services that require them."""
        # Parse service name and arguments
        parts = line.split(None, 1)
        service_name = parts[0] if parts else ""
        args_str = parts[1] if len(parts) > 1 else ""

        available_services = get_device_available_services(self.context.client)
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
                        f"{colorize('Usage:', 'yellow')} {service_name} "
                        f"{' '.join([f'{arg}=<value>' for arg in required_args])}"
                    )
                    print(
                        f"{colorize('Example:', 'yellow')} "
                        f"{service_name} {required_args[0]}=$subscription"
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
                        f"{colorize('Error:', 'red')} "
                        f"Missing required arguments: {', '.join(missing_args)}"
                    )
                    print(
                        f"{colorize('Usage:', 'yellow')} {service_name} "
                        f"{' '.join([f'{arg}=<value>' for arg in required_args])}"
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
                                f"{colorize('Error:', 'red')} "
                                f"Could not resolve reference '{arg_value}'"
                            )
                            return
                        parsed_args[arg_name] = resolved_value

                # Call service method with arguments
                service_method = getattr(self.context.client, service_name)
                service = service_method(**parsed_args)
            else:
                # Service doesn't require arguments
                service = getattr(self.context.client, service_name)()

            self.context.current_service = service
            self.context.current_service_name = service_name
            self.update_prompt()

            print(
                f"{colorize('Entered service:', 'yellow')} {colorize(service_name, 'cyan')}"
            )

            # Show available methods
            methods = get_service_methods(service)
            methods_preview = ", ".join(methods[:10])
            if len(methods) > 10:
                print(
                    f"{colorize('Available methods:', 'yellow')} {methods_preview} ... "
                    f"and {colorize(f'{len(methods) - 10} more.', 'yellow')}"
                )
                print(
                    f"Type {colorize('ls', 'cyan')} or press "
                    f"{colorize('<TAB>', 'yellow')} to see all."
                )
            else:
                print(f"{colorize('Available methods:', 'yellow')} {methods_preview}")
            print(f"Type {colorize('up', 'cyan')} to exit service mode.")

        except (OSError, RuntimeError, ValueError, AttributeError) as e:
            print(f"{colorize('Error entering service:', 'red')} {e}")
            if self.context.args.debug:
                traceback.print_exc()

    def do_exit_service(self, line) -> None:
        """Exit current service mode (alias for 'up')"""
        return self.do_up(line)
