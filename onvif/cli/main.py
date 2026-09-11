"""ONVIF CLI main entry point."""

from __future__ import annotations

import getpass
import sys
import traceback as traceback_lib
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from onvif.cli.helpers import (
    discover_devices,
    execute_command,
    save_output_to_file,
    search_products,
    select_device_interactive,
    setup_warning_format,
)
from onvif.cli.helpers.messages import CLI_EPILOG
from onvif.cli.interactive import InteractiveShell
from onvif.cli.utils import colorize
from onvif.client import ONVIFClient
from onvif.meta import __repository__, __version__
from onvif.operator import CacheMode
from onvif.utils import ONVIFOperationException


def create_parser() -> ArgumentParser:
    """Create argument parser for ONVIF CLI."""
    parser = ArgumentParser(
        prog="onvif",
        description=f"{colorize('ONVIF Terminal Client', 'yellow')} — v{__version__}\n{__repository__}",
        formatter_class=RawDescriptionHelpFormatter,
        epilog=CLI_EPILOG,
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
    parser.add_argument(
        "--interface",
        "-if",
        help="Specify network interface IP for discovery (default: auto-detect)",
    )
    parser.add_argument(
        "--discovery-timeout",
        "-dt",
        type=int,
        default=4,
        help="Discovery timeout in seconds (default: 4)",
    )

    # Product search
    parser.add_argument(
        "--search",
        "-s",
        help="Search ONVIF products database by model or company (e.g., 'c210', 'hikvision')",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="Page number for search results (default: 1)",
    )
    parser.add_argument(
        "--per-page",
        type=int,
        default=20,
        help="Number of results per page (default: 20)",
    )

    # Connection options
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="ONVIF connection timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--digest",
        action="store_true",
        help="Use HTTP Digest instead of WS-Usernametoken",
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
        default=3,
        help="Health check interval in seconds for interactive mode (default: 3)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help=(
            "Save command output to file. Supports .json, .xml extensions for format detection, "
            "or plain text. XML format automatically enables debug mode for SOAP capture."
        ),
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


def main() -> None:
    """Main CLI entry point."""
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
        print(colorize(__version__, "yellow"))
        sys.exit(0)

    # Handle product search
    if args.search:
        search_products(args.search, args.page, args.per_page)
        sys.exit(0)

    # Validate arguments early (before discovery)
    # Skip validation if search mode is active
    if (
        not args.search
        and not args.interactive
        and (not args.service or not args.method)
    ):
        parser.error(
            f"Either {colorize('--interactive', 'white')}/{colorize('-i', 'white')} "
            f"mode or {colorize('service/method', 'white')} must be specified"
        )

    # Validate output argument
    if args.output and args.interactive:
        parser.error(
            f"{colorize('--output', 'white')} cannot be used with {colorize('--interactive', 'white')} mode"
        )

    # Handle discovery mode
    if args.discover:
        if args.host:
            parser.error(
                f"{colorize('--discover', 'white')} cannot be used with {colorize('--host', 'white')}"
            )

        # Discover devices (pass --https flag to prioritize HTTPS XAddrs and filter term)
        devices = discover_devices(
            timeout=args.discovery_timeout,
            interface=args.interface if args.interface else None,
            prefer_https=args.https,
            filter_term=args.filter,
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
        args.host, args.port, _ = selected

        # Use device's detected protocol (already filtered by prefer_https in discover_devices)
        # No need to override - device info already has correct protocol based on --https flag

    # Validate that host is provided (either via --host or --discover) unless using --search
    if not args.search and not args.host:
        parser.error(
            f"Either {colorize('--host', 'white')} or {colorize('--discover', 'white')} must be specified"
        )

    # Handle username prompt (skip for search mode)
    if not args.search and not args.username:
        try:
            args.username = input("Enter username: ")
        except (EOFError, KeyboardInterrupt):
            print("\nUsername entry cancelled.")
            sys.exit(1)

    # Handle password securely if not provided (skip for search mode)
    if not args.search and not args.password:
        try:
            args.password = getpass.getpass(
                f"Enter password for {colorize(f'{args.username}@{args.host}', 'yellow')}: "
            )
        except (EOFError, KeyboardInterrupt):
            print("\nPassword entry cancelled.")
            sys.exit(1)

    # Skip ONVIF client creation for search mode
    if args.search:
        return

    try:
        # Create ONVIF client
        # Auto-enable debug mode if output format is XML
        auto_debug = args.debug or (
            args.output and args.output.lower().endswith(".xml")
        )

        client = ONVIFClient(
            host=args.host,
            port=args.port,
            username=args.username,
            password=args.password,
            http_digest=args.digest,
            timeout=args.timeout,
            cache=CacheMode(args.cache),
            use_https=args.https,
            verify_ssl=not args.no_verify,
            apply_patch=not args.no_patch,
            capture_xml=auto_debug,
            wsdl_dir=args.wsdl,
        )

        if args.interactive:
            # Test connection before starting interactive shell
            try:
                # Try to get device information to verify connection
                client.devicemgmt().GetDeviceInformation()
            except ONVIFOperationException as e:
                print(
                    f"{colorize('Error:', 'red')} Unable to connect to ONVIF device at "
                    f"{colorize(f'{args.host}:{args.port}', 'white')}",
                    file=sys.stderr,
                )
                print(f"Connection error: {e}", file=sys.stderr)
                if args.debug:
                    traceback_lib.print_exc()
                sys.exit(1)

            # Start interactive shell
            shell = InteractiveShell(client, args)
            shell.run()
        else:
            # Execute direct command
            params_str = " ".join(args.params) if args.params else None
            result = execute_command(client, args.service, args.method, params_str)

            # Save output to file if specified
            if args.output:
                # Auto-enable debug mode for XML output
                effective_debug = args.debug or args.output.lower().endswith(".xml")
                save_output_to_file(result, args.output, effective_debug, client)
                print(
                    f"{colorize('Output saved to:', 'green')} {colorize(args.output, 'white')}"
                )
            else:
                print(str(result))

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.debug:
            traceback_lib.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
