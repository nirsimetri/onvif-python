# onvif/cli/main.py

import argparse
import sys
import getpass
from typing import Any, Dict

from ..client import ONVIFClient
from ..operator import CacheMode
from .interactive import InteractiveShell
from .utils import parse_json_params, colorize


def create_parser():
    """Create argument parser for ONVIF CLI"""
    parser = argparse.ArgumentParser(
        prog="onvif",
        description=f"{colorize("ONVIF Terminal Client", 'yellow')} —\nhttps://github.com/nirsimetri/onvif-python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
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
    parser.add_argument(
        "--host", "-H", required=True, help="ONVIF device IP address or hostname"
    )
    parser.add_argument(
        "--port", "-P",
        type=int,
        default=80,
        help="ONVIF device port (default: 80)",
    )
    parser.add_argument("--username", "-u", help="Username for authentication")
    parser.add_argument("--password", "-p", help="Password for authentication")

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

    return parser


def main():
    """Main CLI entry point"""
    parser = create_parser()

    # Check if no arguments provided at all
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_intermixed_args()

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

    # Validate arguments
    if not args.interactive and (not args.service or not args.method):
        parser.error(
            f"Either {colorize('--interactive', 'white')}/{colorize('-i', 'white')} mode or {colorize('service/method', 'white')} must be specified"
        )

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


if __name__ == "__main__":
    main()
