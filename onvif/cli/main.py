# onvif/cli/main.py

import argparse
import sys
import warnings
import getpass
from typing import Any, Optional, Tuple

from ..client import ONVIFClient
from ..operator import CacheMode
from ..utils.discovery import ONVIFDiscovery
from .interactive import InteractiveShell
from .utils import parse_json_params, colorize


def create_parser():
    """Create argument parser for ONVIF CLI"""
    parser = argparse.ArgumentParser(
        prog="onvif",
        description=f"{colorize('ONVIF Terminal Client', 'yellow')} — v0.1.9\nhttps://github.com/nirsimetri/onvif-python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Discover ONVIF devices on network
  {colorize('onvif', 'yellow')} --discover --username admin --password admin123 --interactive
  {colorize('onvif', 'yellow')} media GetProfiles --discover --username admin
  {colorize('onvif', 'yellow')} -d -i

  # Discover with filtering
  {colorize('onvif', 'yellow')} --discover --filter ptz --interactive
  {colorize('onvif', 'yellow')} -d -f "C210" -i
  {colorize('onvif', 'yellow')} -d -f "audio_encoder" -u admin -p admin123 -i

  # Direct command execution
  {colorize('onvif', 'yellow')} devicemgmt GetCapabilities Category=All --host 192.168.1.17 --port 8000 --username admin --password admin123
  {colorize('onvif', 'yellow')} ptz ContinuousMove ProfileToken=Profile_1 Velocity={{"PanTilt": {{"x": -0.1, "y": 0}}}} --host 192.168.1.17 --port 8000 --username admin --password admin123

  # Interactive mode
  {colorize('onvif', 'yellow')} --host 192.168.1.17 --port 8000 --username admin --password admin123 --interactive

  # Prompting for username and password
  # (if not provided)
  {colorize('onvif', 'yellow')} -H 192.168.1.17 -P 8000 -i

  # Using HTTPS
  {colorize('onvif', 'yellow')} media GetProfiles --host camera.example.com --port 443 --username admin --password admin123 --https
        """,
    )

    # Connection parameters
    parser.add_argument("--host", "-H", help="ONVIF device IP address or hostname")
    parser.add_argument(
        "--port",
        "-P",
        type=int,
        default=80,
        help="ONVIF device port (default: 80)",
    )
    parser.add_argument("--username", "-u", help="Username for authentication")
    parser.add_argument("--password", "-p", help="Password for authentication")

    # Device discovery
    parser.add_argument(
        "--discover",
        "-d",
        action="store_true",
        help="Discover ONVIF devices on the network using WS-Discovery",
    )
    parser.add_argument(
        "--filter",
        "-f",
        help="Filter discovered devices by types or scopes (case-insensitive substring match)",
    )

    # Connection options
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="Connection timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--https", action="store_true", help="Use HTTPS instead of HTTP"
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Disable SSL certificate verification",
    )
    parser.add_argument("--no-patch", action="store_true", help="Disable ZeepPatcher")

    # CLI options
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Start interactive mode"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode with XML capture"
    )
    parser.add_argument("--wsdl", help="Custom WSDL directory path")
    parser.add_argument(
        "--cache",
        choices=[mode.value for mode in CacheMode],
        default=CacheMode.ALL.value,
        help="Caching mode for ONVIFClient (default: all). "
        "'all': memory+disk, 'db': disk-only, 'mem': memory-only, 'none': disabled.",
    )
    parser.add_argument(
        "--health-check-interval",
        "-hci",
        type=int,
        default=10,
        help="Health check interval in seconds for interactive mode (default: 10)",
    )

    # Service and method (for direct command execution)
    parser.add_argument(
        "service", nargs="?", help="ONVIF service name (e.g., devicemgmt, media, ptz)"
    )
    parser.add_argument(
        "method",
        nargs="?",
        help="Service method name (e.g., GetCapabilities, GetProfiles)",
    )
    parser.add_argument(
        "params", nargs="*", help="Method parameters as Simple Parameter or JSON string"
    )

    # ONVI CLI
    parser.add_argument(
        "--version", "-v", action="store_true", help="Show ONVIF CLI version and exit"
    )

    return parser


def main():
    """Main CLI entry point"""
    # Setup custom warning format for cleaner output
    setup_warning_format()

    parser = create_parser()

    # Check if no arguments provided at all
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_intermixed_args()

    # Show ONVIF CLI version
    if args.version:
        print(colorize("0.1.9", "yellow"))
        sys.exit(0)

    # Validate arguments early (before discovery)
    if not args.interactive and (not args.service or not args.method):
        parser.error(
            f"Either {colorize('--interactive', 'white')}/{colorize('-i', 'white')} mode or {colorize('service/method', 'white')} must be specified"
        )

    # Handle discovery mode
    if args.discover:
        if args.host:
            parser.error(
                f"{colorize('--discover', 'white')} cannot be used with {colorize('--host', 'white')}"
            )

        # Discover devices (pass --https flag to prioritize HTTPS XAddrs and filter term)
        devices = discover_devices(
            timeout=4, prefer_https=args.https, filter=args.filter
        )

        if not devices:
            if args.filter:
                print(
                    f"{colorize('No devices found matching filter:', 'red')} {colorize(args.filter, 'white')}"
                )
            else:
                print(colorize("No ONVIF devices discovered. Exiting.", "red"))
            sys.exit(1)

        # Let user select a device
        selected = select_device_interactive(devices)

        if selected is None:
            print(colorize("Device selection cancelled.", "cyan"))
            sys.exit(0)

        # Set host, port, and HTTPS from selected device
        args.host, args.port, device_use_https = selected

        # Use device's detected protocol (already filtered by prefer_https in discover_devices)
        # No need to override - device info already has correct protocol based on --https flag

    # Validate that host is provided (either via --host or --discover)
    if not args.host:
        parser.error(
            f"Either {colorize('--host', 'white')} or {colorize('--discover', 'white')} must be specified"
        )

    # Handle username prompt
    if not args.username:
        try:
            args.username = input("Enter username: ")
        except (EOFError, KeyboardInterrupt):
            print("\nUsername entry cancelled.")
            sys.exit(1)

    # Handle password securely if not provided
    if not args.password:
        try:
            args.password = getpass.getpass(
                f"Enter password for {colorize(f'{args.username}@{args.host}', 'yellow')}: "
            )
        except (EOFError, KeyboardInterrupt):
            print("\nPassword entry cancelled.")
            sys.exit(1)

    try:
        # Create ONVIF client
        client = ONVIFClient(
            host=args.host,
            port=args.port,
            username=args.username,
            password=args.password,
            timeout=args.timeout,
            cache=CacheMode(args.cache),
            use_https=args.https,
            verify_ssl=not args.no_verify,
            apply_patch=not args.no_patch,
            capture_xml=args.debug,
            wsdl_dir=args.wsdl,
        )

        if args.interactive:
            # Test connection before starting interactive shell
            try:
                # Try to get device information to verify connection
                client.devicemgmt().GetDeviceInformation()
            except Exception as e:
                print(
                    f"{colorize('Error:', 'red')} Unable to connect to ONVIF device at {colorize(f'{args.host}:{args.port}', 'white')}",
                    file=sys.stderr,
                )
                print(f"Connection error: {e}", file=sys.stderr)
                if args.debug:
                    import traceback

                    traceback.print_exc()
                sys.exit(1)

            # Start interactive shell
            shell = InteractiveShell(client, args)
            shell.run()
        else:
            # Execute direct command
            params_str = " ".join(args.params) if args.params else None
            result = execute_command(client, args.service, args.method, params_str)
            print(str(result))

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def execute_command(
    client: ONVIFClient, service_name: str, method_name: str, params_str: str = None
) -> Any:
    """Execute a single ONVIF command"""
    # Get service instance
    try:
        service = getattr(client, service_name.lower())()
    except AttributeError:
        raise ValueError(f"{colorize('Unknown service:', 'red')} {service_name}")

    # Get method
    try:
        method = getattr(service, method_name)
    except AttributeError:
        raise ValueError(
            f"{colorize('Unknown method', 'red')} '{method_name}' for service '{service_name}'"
        )

    # Parse parameters
    params = parse_json_params(params_str) if params_str else {}

    # Execute method
    return method(**params)


def discover_devices(
    timeout: int = 4, prefer_https: bool = False, filter: Optional[str] = None
) -> list:
    """Discover ONVIF devices on the network using WS-Discovery.

    Args:
        timeout: Discovery timeout in seconds
        prefer_https: If True, prioritize HTTPS XAddrs when available
        filter: Optional search term to filter devices by types or scopes

    Returns:
        List of discovered devices with connection info
    """

    # Use ONVIFDiscovery class
    discovery = ONVIFDiscovery(timeout=timeout)

    print(f"\n{colorize('Discovering ONVIF devices on network...', 'yellow')}")
    print(f"Network interface: {colorize(discovery._get_local_ip(), 'white')}")
    print(f"Timeout: {timeout}s")
    if filter:
        print(f"Filter: {colorize(filter, 'yellow')}")
    print()

    devices = discovery.discover(prefer_https=prefer_https, search=filter)

    return devices


def select_device_interactive(devices: list) -> Optional[Tuple[str, int, bool]]:
    """Display devices and allow user to select one interactively.

    Returns:
        Tuple of (host, port, use_https) or None if cancelled
    """
    if not devices:
        print(f"\n{colorize('No ONVIF devices found.', 'red')}")
        return None

    print(f"{colorize(f'Found {len(devices)} ONVIF device(s):', 'green')}")

    for idx, device in enumerate(devices, 1):
        idx_str = colorize(f"[{idx}]", "yellow")
        protocol = "https" if device.get("use_https", False) else "http"
        host_port = f"{device['host']}:{device['port']}"
        protocol_indicator = (
            colorize("🔒 HTTPS", "green")
            if device.get("use_https", False)
            else colorize("HTTP", "white")
        )
        print(f"\n{idx_str} {colorize(host_port, 'yellow')} ({protocol_indicator})")

        # Remove uuid: or urn:uuid: prefix from EPR
        epr_display = device["epr"]
        if epr_display.startswith("urn:uuid:"):
            epr_display = epr_display.replace("urn:uuid:", "")
        elif epr_display.startswith("uuid:"):
            epr_display = epr_display.replace("uuid:", "")
        print(f"    [id] {epr_display}")

        if device["xaddrs"]:
            xaddrs_parts = [f"[{xaddr}]" for xaddr in device["xaddrs"]]
            print(f"    [xaddrs] {' '.join(xaddrs_parts)}")

        if device["types"]:
            types_parts = [f"[{t}]" for t in device["types"]]
            print(f"    [types] {' '.join(types_parts)}")

        if device["scopes"]:
            scope_parts = []
            for scope in device["scopes"]:
                # Remove the prefix "onvif://www.onvif.org/" if present
                if scope.startswith("onvif://www.onvif.org/"):
                    simplified = scope.replace("onvif://www.onvif.org/", "")
                    scope_parts.append(f"[{simplified}]")
                else:
                    # Keep other scopes as-is (e.g., http:123)
                    scope_parts.append(f"[{scope}]")

            if scope_parts:
                print(f"    [scopes] {' '.join(scope_parts)}")

    # Simple selection (without arrow keys for cross-platform compatibility)
    while True:
        try:
            selection = input(
                f"\nSelect device number {colorize(f'1-{len(devices)}', 'white')} or {colorize('q', 'white')} to quit: "
            )

            if selection.lower() == "q":
                return None

            idx = int(selection)
            if 1 <= idx <= len(devices):
                selected = devices[idx - 1]
                protocol = "https" if selected.get("use_https", False) else "http"
                host_port = f"{selected['host']}:{selected['port']}"
                print(
                    f"\n{colorize('Selected:', 'green')} {colorize(protocol, 'cyan')}://{colorize(host_port, 'yellow')}"
                )
                return (
                    selected["host"],
                    selected["port"],
                    selected.get("use_https", False),
                )
            else:
                print(colorize("Invalid selection. Please try again.", "red"))

        except ValueError:
            print(colorize("Invalid input. Please enter a number.", "red"))
        except (EOFError, KeyboardInterrupt):
            return None


def setup_warning_format():
    """Setup custom warning format to show clean, concise warnings"""

    def custom_warning_format(message, category, filename, lineno, line=None):
        # Show only the warning message without file path and line number
        return f"{category.__name__}: {message}\n"

    warnings.formatwarning = custom_warning_format


if __name__ == "__main__":
    main()
