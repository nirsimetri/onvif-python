# onvif/cli/main.py

import argparse
import sys
import warnings
import getpass
from typing import Any, Optional, Tuple

from ..client import ONVIFClient
from ..operator import CacheMode
from .interactive import InteractiveShell
from .utils import parse_json_params, colorize


def create_parser():
    """Create argument parser for ONVIF CLI"""
    parser = argparse.ArgumentParser(
        prog="onvif",
        description=f"{colorize('ONVIF Terminal Client', 'yellow')} — v0.1.5\nhttps://github.com/nirsimetri/onvif-python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Discover ONVIF devices on network
  {colorize('onvif', 'yellow')} --discover --username admin --password admin123 --interactive
  {colorize('onvif', 'yellow')} media GetProfiles --discover --username admin
  {colorize('onvif', 'yellow')} -d -i

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
        print(colorize("0.1.5", "yellow"))
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

        # Discover devices (pass --https flag to prioritize HTTPS XAddrs)
        devices = discover_devices(timeout=4, prefer_https=args.https)

        if not devices:
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


def discover_devices(timeout: int = 4, prefer_https: bool = False) -> list:
    """Discover ONVIF devices on the network using WS-Discovery.

    Args:
        timeout: Discovery timeout in seconds
        prefer_https: If True, prioritize HTTPS XAddrs when available

    Returns:
        List of discovered devices with connection info
    """
    import socket
    import uuid
    import xml.etree.ElementTree as ET
    import struct

    WS_DISCOVERY_PORT = 3702
    WS_DISCOVERY_ADDRESS_IPv4 = "239.255.255.250"

    # WS-Discovery Probe message
    WS_DISCOVERY_PROBE_MESSAGE = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" '
        'xmlns:tds="http://www.onvif.org/ver10/device/wsdl" '
        'xmlns:tns="http://schemas.xmlsoap.org/ws/2005/04/discovery" '
        'xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing">'
        "<soap:Header>"
        "<wsa:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</wsa:Action>"
        "<wsa:MessageID>urn:uuid:{uuid}</wsa:MessageID>"
        "<wsa:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</wsa:To>"
        "</soap:Header>"
        "<soap:Body>"
        "<tns:Probe>"
        "<tns:Types>tds:Device</tns:Types>"
        "</tns:Probe>"
        "</soap:Body>"
        "</soap:Envelope>"
    )

    # Get local network interface
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "0.0.0.0"

    print(f"\n{colorize('Discovering ONVIF devices on network...', 'yellow')}")
    print(f"Network interface: {colorize(local_ip, 'white')}")
    print(f"Timeout: {timeout}s\n")

    probe_uuid = str(uuid.uuid4())
    probe = WS_DISCOVERY_PROBE_MESSAGE.format(uuid=probe_uuid)

    responses = []

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((local_ip, 0))
        sock.settimeout(timeout)

        ttl = struct.pack("b", 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

        sock.sendto(
            probe.encode("utf-8"), (WS_DISCOVERY_ADDRESS_IPv4, WS_DISCOVERY_PORT)
        )

        while True:
            try:
                data, addr = sock.recvfrom(8192)
                response = data.decode("utf-8", errors="ignore").strip()

                if response and len(response) > 10:
                    if response.startswith("<?xml") or response.startswith("<"):
                        responses.append({"xml": response, "address": addr[0]})

            except socket.timeout:
                break
            except Exception:
                break

        sock.close()

    except Exception as e:
        print(f"{colorize('Error during discovery:', 'red')} {e}")
        return []

    # Parse responses
    devices = []
    namespaces = {
        "soap": "http://www.w3.org/2003/05/soap-envelope",
        "wsa": "http://schemas.xmlsoap.org/ws/2004/08/addressing",
        "wsd": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
        "d": "http://schemas.xmlsoap.org/ws/2005/04/discovery",
    }

    for resp in responses:
        try:
            root = ET.fromstring(resp["xml"])
            probe_match = root.find(".//d:ProbeMatch", namespaces) or root.find(
                ".//wsd:ProbeMatch", namespaces
            )

            if probe_match is None:
                continue

            device_info = {
                "epr": "",
                "types": [],
                "scopes": [],
                "xaddrs": [],
                "host": None,
                "port": 80,
                "use_https": False,  # Auto-detect HTTPS from XAddrs
            }

            epr = probe_match.find(".//wsa:EndpointReference/wsa:Address", namespaces)
            if epr is not None:
                device_info["epr"] = epr.text

            types_elem = probe_match.find(".//d:Types", namespaces) or probe_match.find(
                ".//wsd:Types", namespaces
            )
            if types_elem is not None and types_elem.text:
                device_info["types"] = types_elem.text.split()

            scopes_elem = probe_match.find(
                ".//d:Scopes", namespaces
            ) or probe_match.find(".//wsd:Scopes", namespaces)
            if scopes_elem is not None and scopes_elem.text:
                device_info["scopes"] = scopes_elem.text.split()

            xaddrs_elem = probe_match.find(
                ".//d:XAddrs", namespaces
            ) or probe_match.find(".//wsd:XAddrs", namespaces)
            if xaddrs_elem is not None and xaddrs_elem.text:
                device_info["xaddrs"] = xaddrs_elem.text.split()

                # Extract host, port, and protocol from XAddrs
                # Use prefer_https parameter to decide which XAddr to use
                if device_info["xaddrs"]:
                    # Select XAddr based on prefer_https flag
                    if prefer_https:
                        # Try to find HTTPS XAddr first if prefer_https=True
                        https_xaddr = next(
                            (
                                x
                                for x in device_info["xaddrs"]
                                if x.startswith("https://")
                            ),
                            None,
                        )
                        xaddr = https_xaddr or device_info["xaddrs"][0]
                    else:
                        # Use first XAddr (usually HTTP) if prefer_https=False
                        xaddr = device_info["xaddrs"][0]

                    if "://" in xaddr:
                        # Detect protocol
                        protocol = xaddr.split("://")[0]
                        device_info["use_https"] = protocol == "https"

                        # Extract host and port
                        parts = xaddr.split("://")[1].split("/")[0]
                        if ":" in parts:
                            device_info["host"] = parts.split(":")[0]
                            device_info["port"] = int(parts.split(":")[1])
                        else:
                            device_info["host"] = parts
                            # Set default port based on protocol
                            device_info["port"] = 443 if protocol == "https" else 80

            if device_info["host"]:
                devices.append(device_info)

        except Exception:
            continue

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
        print(f"    [id] {device['epr']}")

        if device["xaddrs"]:
            xaddrs_str = " ".join(device["xaddrs"])
            print(f"    [xaddrs] {xaddrs_str}")

        if device["types"]:
            types_str = " ".join(device["types"])
            print(f"    [types] {types_str}")

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
