"""ONVIF Interactive Shelll implementation."""

import cmd
import sys

from requests.exceptions import RequestException
from zeep.exceptions import TransportError

from onvif.cli.helpers.messages import print_interactive_intro
from onvif.cli.utils import colorize, get_device_available_services
from onvif.client import ONVIFClient
from onvif.utils.exceptions import ONVIFOperationException

from .context import ShellContext
from .information import InformationCommands
from .navigation import NavigationCommands
from .reference import ReferenceCommands
from .service import ServiceCommands
from .utils import ShellUtilities


class InteractiveShell(
    ShellUtilities,
    ServiceCommands,
    InformationCommands,
    ReferenceCommands,
    NavigationCommands,
    cmd.Cmd,
):
    """Interactive ONVIF CLI shell."""

    def __init__(self, client: ONVIFClient, args):
        cmd.Cmd.__init__(self)

        self.context = ShellContext(client=client, args=args)

        self._initialize_health_check()

        # Enable tab completion
        # for Windows will use pyreadline3 to install readline module
        # pylint: disable=import-outside-toplevel
        try:
            import readline

            # Set completer to this instance
            readline.set_completer(self.complete)  # type: ignore[attr-defined, arg-type]
            readline.set_completer_delims(" \t\n`!@#$%^&*()=+[{]}\\|;:'\",<>?")  # type: ignore[attr-defined]

            # Enable tab completion, making it compatible with both GNU readline and libedit
            if (
                hasattr(readline, "__doc__")
                and readline.__doc__
                and "libedit" in readline.__doc__
            ):
                readline.parse_and_bind("bind ^I rl_complete")  # type: ignore[attr-defined]
            else:
                readline.parse_and_bind("tab: complete")  # type: ignore[attr-defined]
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
            self.device_data = self.context.client.devicemgmt().GetDeviceInformation()
            manufacturer = getattr(self.device_data, "Manufacturer", "Unknown")
            model = getattr(self.device_data, "Model", "Unknown")
            firmware = getattr(self.device_data, "FirmwareVersion", "Unknown")
            serial = getattr(self.device_data, "SerialNumber", "Unknown")
            hardware_id = getattr(self.device_data, "HardwareId", "Unknown")

            # Get latest supported ONVIF version
            supported_versions = self.context.client.devicemgmt().GetCapabilities(
                Category="All"
            )["Device"]["System"]["SupportedVersions"]
            if supported_versions:
                latest_version = max(
                    supported_versions,
                    key=lambda version: (
                        getattr(version, "Major", 0),
                        getattr(version, "Minor", 0),
                    ),
                )

                major = getattr(latest_version, "Major", "")
                minor = getattr(latest_version, "Minor", "")

                if major != "":
                    onvif_version = (
                        f"{major}.{minor} {colorize('[Latest]', 'green')}"
                        if minor != ""
                        else str(major)
                    )
        except (ONVIFOperationException, KeyError, AttributeError) as e:
            if isinstance(e, ONVIFOperationException):
                if isinstance(e.original_exception, (RequestException, TransportError)):
                    self._handle_connection_error()
            else:
                # For other errors (e.g., GetCapabilities not supported), we can still proceed
                # with basic device info if GetDeviceInformation succeeded.
                pass

        self.context.device_info_text = (
            f"\n\n{colorize('[Device Info]', 'cyan')}\n"
            f"  Manufacturer  : {colorize(manufacturer, 'white')}\n"
            f"  Model         : {colorize(model, 'white')}\n"
            f"  Firmware      : {colorize(firmware, 'white')}\n"
            f"  Serial        : {colorize(serial, 'white')}\n"
            f"  HardwareId    : {colorize(hardware_id, 'white')}\n"
            f"  ONVIF Version : {colorize(onvif_version, 'white')}"
        )

        self.intro = print_interactive_intro(args, self.context.device_info_text)

        # Start background health check after successful initialization
        self.health_check_thread.start()

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
        if self.context.current_service and line and not line.startswith("do_"):
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
        available_services = get_device_available_services(self.context.client)

        # Check if it's a service call (with or without arguments)
        # Extract first word to check if it's a service name
        first_word = line.split()[0] if line.split() else line

        if first_word in available_services:
            return self.do_enter_service(line)

        # Check if the whole line (without arguments) is a service
        if line in available_services:
            return self.do_enter_service(line)

        # Check if it's a method call in service context
        if self.context.current_service:
            if self.context.current_service and " " in line:
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

        return None

    def emptyline(self):
        """Handle empty line."""

    def do_clear(self, _line):
        """Clear terminal screen."""
        if sys.platform == "win32":
            print("\033[2J\033[3J\033[H", end="")
        else:
            print("\033[2J\033[H", end="")

    def do_exit(self, _line):
        """Exit the shell."""
        self.stop_health_check.set()
        print(colorize("Goodbye!", "cyan"))
        return True

    def run(self):
        """Run the interactive shell."""
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print(f"\n{colorize('Goodbye!', 'cyan')}")
            self.stop_health_check.set()
            sys.exit(0)
