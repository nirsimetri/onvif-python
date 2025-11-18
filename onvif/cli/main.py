# onvif/cli/main.py

import argparse
import sys
import warnings
import getpass
import sqlite3
import os
import shutil
import json
from datetime import datetime
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
        description=f"{colorize('ONVIF Terminal Client', 'yellow')} — v0.2.6\nhttps://github.com/nirsimetri/onvif-python",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Product search
  {colorize('onvif', 'yellow')} --search c210
  {colorize('onvif', 'yellow')} -s "axis camera"
  {colorize('onvif', 'yellow')} --search hikvision --page 2 --per-page 5

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
  {colorize('onvif', 'yellow')} ptz ContinuousMove ProfileToken=Profile_1 Velocity={{'PanTilt': {{'x': -0.1, 'y': 0}}}} -H 192.168.1.17 -P 8000 -u admin -p admin123

  # Save output to file
  {colorize('onvif', 'yellow')} devicemgmt GetDeviceInformation --host 192.168.1.17 --port 8000 --username admin --password admin123 --output device_info.json
  {colorize('onvif', 'yellow')} media GetProfiles --host 192.168.1.17 --port 8000 --username admin --password admin123 --output profiles.xml
  {colorize('onvif', 'yellow')} ptz GetConfigurations --host 192.168.1.17 --port 8000 --username admin --password admin123 --output ptz_config.txt --debug

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
    parser.add_argument(
        "--output",
        "-o",
        help="Save command output to file. Supports .json, .xml extensions for format detection, or plain text. XML format automatically enables debug mode for SOAP capture.",
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
        print(colorize("0.2.6", "yellow"))
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
            f"Either {colorize('--interactive', 'white')}/{colorize('-i', 'white')} mode or {colorize('service/method', 'white')} must be specified"
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
            timeout=4, prefer_https=args.https, filter_term=args.filter
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


def save_output_to_file(
    result: Any, output_path: str, debug_mode: bool, client: ONVIFClient
) -> None:
    """Save command output to file in appropriate format based on file extension.

    Args:
        result: The ONVIF command result
        output_path: Path to output file
        debug_mode: Whether debug mode is enabled (for XML capture)
        client: ONVIFClient instance (for accessing XML plugin)
    """
    try:
        # Determine output format based on file extension
        _, ext = os.path.splitext(output_path.lower())

        if ext == ".json":
            # Prepare output data
            output_data = {}

            # JSON format
            output_data["result"] = _serialize_for_json(result)
            output_data["timestamp"] = datetime.now().isoformat()
            output_data["raw_result"] = str(result)  # Add raw string as fallback

            # Add XML data if debug mode is enabled and XML plugin is available
            if debug_mode and client.xml_plugin:
                output_data["debug"] = {
                    "last_request_xml": client.xml_plugin.last_sent_xml,
                    "last_response_xml": client.xml_plugin.last_received_xml,
                    "last_operation": client.xml_plugin.last_operation,
                }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

        elif ext == ".xml":
            # XML format - prioritize raw SOAP XML over parsed result
            if client.xml_plugin and client.xml_plugin.last_received_xml:
                # Save the raw SOAP response XML with minimal wrapper
                content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- ONVIF SOAP Response -->
<!-- Timestamp: {datetime.now().isoformat()} -->
<!-- Operation: {client.xml_plugin.last_operation or 'Unknown'} -->

{client.xml_plugin.last_received_xml}
"""
            else:
                # Fallback: Simple XML wrapper for the parsed result
                content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- ONVIF Command Output (Parsed Result) -->
<!-- Timestamp: {datetime.now().isoformat()} -->
<!-- Note: Raw SOAP XML not available. Enable --debug for full SOAP capture. -->
<onvif_result>
<![CDATA[
{str(result)}
]]>
</onvif_result>
"""

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        else:
            # Plain text format (default)
            content = "ONVIF Command Output\n"
            content += f"Timestamp: {datetime.now().isoformat()}\n"
            content += f"{'='*50}\n\n"
            content += str(result)

            # Add debug information if available
            if debug_mode and client.xml_plugin:
                content += f"\n\n{'='*50}\n"
                content += "DEBUG INFORMATION\n"
                content += f"{'='*50}\n"
                if client.xml_plugin.last_operation:
                    content += f"Operation: {client.xml_plugin.last_operation}\n\n"
                if client.xml_plugin.last_sent_xml:
                    content += "SOAP Request:\n"
                    content += client.xml_plugin.last_sent_xml + "\n\n"
                if client.xml_plugin.last_received_xml:
                    content += "SOAP Response:\n"
                    content += client.xml_plugin.last_received_xml + "\n"

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

    except Exception as e:
        print(f"{colorize('Error saving output:', 'red')} {e}", file=sys.stderr)
        # Still print the result to console if file save fails
        print(str(result))


def _serialize_for_json(obj: Any) -> Any:
    """Recursively serialize ONVIF objects for JSON output.

    Args:
        obj: Object to serialize

    Returns:
        JSON-serializable representation of the object
    """
    if obj is None:
        return None
    elif isinstance(obj, (str, int, float, bool)):
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (list, tuple)):
        return [_serialize_for_json(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _serialize_for_json(value) for key, value in obj.items()}

    # Check if this is a Zeep object (has _xsd_type attribute)
    elif hasattr(obj, "_xsd_type"):
        result = {}
        # Try to get all elements from XSD type
        if hasattr(obj._xsd_type, "elements"):
            for elem_name, elem_obj in obj._xsd_type.elements:
                try:
                    value = getattr(obj, elem_name, None)
                    if value is not None:
                        result[elem_name] = _serialize_for_json(value)
                except (AttributeError, TypeError):
                    # Skip elements that can't be accessed or have type issues
                    pass

        # Also try regular attributes
        for attr_name in dir(obj):
            if not attr_name.startswith("_") and not callable(
                getattr(obj, attr_name, None)
            ):
                try:
                    attr_value = getattr(obj, attr_name)
                    if attr_value is not None and attr_name not in result:
                        result[attr_name] = _serialize_for_json(attr_value)
                except (AttributeError, TypeError):
                    # Skip attributes that can't be accessed or have type issues
                    pass

        return result

    elif hasattr(obj, "__dict__"):
        # Handle regular objects with attributes
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith("_"):  # Skip private attributes
                result[key] = _serialize_for_json(value)

        # If result is empty, try to get attributes using dir()
        if not result:
            for attr_name in dir(obj):
                if not attr_name.startswith("_") and not callable(
                    getattr(obj, attr_name, None)
                ):
                    try:
                        attr_value = getattr(obj, attr_name)
                        if attr_value is not None:
                            result[attr_name] = _serialize_for_json(attr_value)
                    except (AttributeError, TypeError):
                        # Skip attributes that can't be accessed or have type issues
                        pass

        return result
    elif hasattr(obj, "_value_1"):
        # Handle zeep objects with special structure
        return _serialize_for_json(obj._value_1)
    else:
        # Try to convert to dict using vars() if available
        try:
            obj_dict = vars(obj)
            return _serialize_for_json(obj_dict)
        except TypeError:
            # Fallback to string representation
            return str(obj)


def discover_devices(
    timeout: int = 4, prefer_https: bool = False, filter_term: Optional[str] = None
) -> list:
    """Discover ONVIF devices on the network using WS-Discovery.

    Args:
        timeout: Discovery timeout in seconds
        prefer_https: If True, prioritize HTTPS XAddrs when available
        filter_term: Optional search term to filter devices by types or scopes

    Returns:
        List of discovered devices with connection info
    """

    # Use ONVIFDiscovery class
    discovery = ONVIFDiscovery(timeout=timeout)

    print(f"\n{colorize('Discovering ONVIF devices on network...', 'yellow')}")
    print(f"Network interface: {colorize(discovery._get_local_ip(), 'white')}")
    print(f"Timeout: {timeout}s")
    if filter_term:
        print(f"Filter: {colorize(filter_term, 'yellow')}")
    print()

    devices = discovery.discover(prefer_https=prefer_https, search=filter_term)

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


def search_products(search_term: str, page: int = 1, per_page: int = 20) -> None:
    """Search ONVIF products database and display results in table format with pagination.

    Args:
        search_term: Search term to match against model, post_title, and company_name fields
        page: Page number (1-based)
        per_page: Number of results per page
    """
    # Get the database path relative to the script location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, "..", "db", "products.db")
    db_path = os.path.normpath(db_path)

    if not os.path.exists(db_path):
        print(f"{colorize('Error:', 'red')} Products database not found at {db_path}")
        sys.exit(1)

    # Validate pagination parameters
    if page < 1:
        print(f"{colorize('Error:', 'red')} Page number must be 1 or greater")
        sys.exit(1)

    if per_page < 1 or per_page > 100:
        print(f"{colorize('Error:', 'red')} Per-page must be between 1 and 100")
        sys.exit(1)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # First, get total count for pagination info
        count_query = """
        SELECT COUNT(*)
        FROM onvif_products
        WHERE LOWER(model) LIKE LOWER(?)
           OR LOWER(post_title) LIKE LOWER(?)
           OR LOWER(company_name) LIKE LOWER(?)
           OR LOWER(product_category) LIKE LOWER(?)
        """

        search_pattern = f"%{search_term}%"
        cursor.execute(
            count_query,
            (search_pattern, search_pattern, search_pattern, search_pattern),
        )
        total_count = cursor.fetchone()[0]

        if total_count == 0:
            print(
                f"{colorize('No products found matching:', 'yellow')} {colorize(search_term, 'white')}"
            )
            return

        # Calculate pagination
        total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
        if page > total_pages:
            print(
                f"{colorize('Error:', 'red')} Page {page} does not exist. Total pages: {total_pages}"
            )
            return

        offset = (page - 1) * per_page

        # Search query with pagination
        query = """
        SELECT ID, test_date, post_title, product_firmware_version,
               product_profiles, product_category, type,
               company_name
        FROM onvif_products
        WHERE LOWER(model) LIKE LOWER(?)
           OR LOWER(post_title) LIKE LOWER(?)
           OR LOWER(company_name) LIKE LOWER(?)
           OR LOWER(product_category) LIKE LOWER(?)
        ORDER BY test_date DESC
        LIMIT ? OFFSET ?
        """

        cursor.execute(
            query,
            (
                search_pattern,
                search_pattern,
                search_pattern,
                search_pattern,
                per_page,
                offset,
            ),
        )
        results = cursor.fetchall()

        # Display results in table format
        start_result = offset + 1
        end_result = min(offset + per_page, total_count)
        print(
            f"\n{colorize(f'Found {total_count} product(s) matching:', 'green')} {colorize(search_term, 'white')}"
        )
        print(
            f"{colorize(f'Showing {start_result}-{end_result} of {total_count} results', 'cyan')}"
        )
        print()

        # Table headers
        headers = [
            "ID",
            "Test Date",
            "Model",
            "Firmware",
            "Profiles",
            "Category",
            "Type",
            "Company",
        ]

        # Get terminal width for adaptive formatting
        try:
            terminal_width = shutil.get_terminal_size().columns
        except Exception:
            terminal_width = 120  # fallback width

        # Calculate minimum column widths
        min_col_widths = [max(len(str(header)), 8) for header in headers]

        # Calculate actual content widths (without truncation first)
        actual_widths = [0] * len(headers)
        for row in results:
            for i, value in enumerate(row):
                if value:
                    if i == 1:  # Date column - calculate formatted date width
                        str_value = str(value)
                        if "T" in str_value:
                            date_part = str_value.split("T")[0]
                            time_part = str_value.split("T")[1].split(".")[0]
                            if "+" in time_part:
                                time_part = time_part.split("+")[0]
                            elif "Z" in time_part:
                                time_part = time_part.replace("Z", "")
                            formatted_date = f"{date_part} {time_part}"
                            actual_widths[i] = max(
                                actual_widths[i], len(formatted_date)
                            )
                        else:
                            actual_widths[i] = max(actual_widths[i], len(str_value))
                    else:
                        actual_widths[i] = max(actual_widths[i], len(str(value)))

        # Combine minimum widths with actual content widths
        col_widths = [
            max(min_col_widths[i], actual_widths[i]) for i in range(len(headers))
        ]

        # Calculate space needed for separators (3 chars per separator: " | ")
        separator_space = (len(headers) - 1) * 3
        total_content_width = sum(col_widths)
        total_needed_width = total_content_width + separator_space

        # If table is too wide for terminal, apply smart truncation
        if total_needed_width > terminal_width:
            available_width = terminal_width - separator_space

            # Priority columns that should not be truncated (ID, Date)
            protected_cols = {0, 1}  # ID and Date columns
            protected_width = sum(col_widths[i] for i in protected_cols)

            # Width available for other columns
            remaining_width = available_width - protected_width

            # Columns that can be truncated
            truncatable_cols = [
                i for i in range(len(headers)) if i not in protected_cols
            ]

            if remaining_width > 0 and truncatable_cols:
                # Calculate proportional allocation for truncatable columns
                current_truncatable_width = sum(col_widths[i] for i in truncatable_cols)

                for i in truncatable_cols:
                    if current_truncatable_width > 0:
                        # Proportional allocation
                        proportion = col_widths[i] / current_truncatable_width
                        new_width = int(remaining_width * proportion)

                        # Ensure minimum width
                        col_widths[i] = max(new_width, min_col_widths[i])
                    else:
                        col_widths[i] = min_col_widths[i]

        # Print header
        header_line = " | ".join(
            header.ljust(col_widths[i]) for i, header in enumerate(headers)
        )
        print(colorize(header_line, "yellow"))
        print(colorize("-" * len(header_line), "white"))

        # Print data rows
        for row in results:
            formatted_row = []
            for i, value in enumerate(row):
                if value is None:
                    formatted_value = ""
                else:
                    str_value = str(value)

                    # Special formatting for date column (index 1)
                    if i == 1 and value:  # Date column
                        try:
                            # Handle ISO format with timezone
                            if "T" in str_value:
                                # Parse ISO format: 2024-08-15T17:53:12.9154121+08:00
                                # Extract just the date and time part before timezone
                                date_part = str_value.split("T")[0]
                                time_part = str_value.split("T")[1].split(".")[
                                    0
                                ]  # Remove microseconds
                                if "+" in time_part:
                                    time_part = time_part.split("+")[0]
                                elif "Z" in time_part:
                                    time_part = time_part.replace("Z", "")
                                formatted_value = f"{date_part} {time_part}"
                            elif (
                                len(str_value) == 19 and " " in str_value
                            ):  # Already in correct format
                                formatted_value = str_value
                            elif len(str_value) == 10:  # Just date, add time
                                formatted_value = f"{str_value} 00:00:00"
                            else:
                                # Try to parse common formats
                                try:
                                    parsed_date = datetime.strptime(
                                        str_value, "%Y-%m-%d %H:%M:%S"
                                    )
                                    formatted_value = parsed_date.strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    )
                                except ValueError:
                                    try:
                                        parsed_date = datetime.strptime(
                                            str_value, "%Y-%m-%d"
                                        )
                                        formatted_value = parsed_date.strftime(
                                            "%Y-%m-%d 00:00:00"
                                        )
                                    except ValueError:
                                        formatted_value = (
                                            str_value  # Keep original if parsing fails
                                        )
                        except Exception:
                            formatted_value = str_value  # Keep original if any error
                    else:
                        # Apply truncation based on calculated column width
                        max_width = col_widths[i]
                        if len(str_value) > max_width:
                            formatted_value = str_value[: max_width - 3] + "..."
                        else:
                            formatted_value = str_value

                formatted_row.append(formatted_value.ljust(col_widths[i]))

            print(" | ".join(formatted_row))

        # Display pagination information
        print()
        newline = "\n" if total_pages == 1 else ""
        print(f"{colorize(f'Page {page} of {total_pages}', 'cyan')} {newline}")

        # Show navigation hints
        nav_hints = []
        if page > 1:
            nav_hints.append(f"Previous: --page {page - 1}")
        if page < total_pages:
            nav_hints.append(f"Next: --page {page + 1}")

        if nav_hints:
            print(f"{colorize('Navigation:', 'white')} {' | '.join(nav_hints)}\n")

        conn.close()

    except sqlite3.Error as e:
        print(f"{colorize('Database error:', 'red')} {e}")
        sys.exit(1)
    except Exception as e:
        print(f"{colorize('Error:', 'red')} {e}")
        sys.exit(1)


def setup_warning_format():
    """Setup custom warning format to show clean, concise warnings"""

    def custom_warning_format(message, category, filename, lineno, line=None):
        # Show only the warning message without file path and line number
        return f"{category.__name__}: {message}\n"

    warnings.formatwarning = custom_warning_format


if __name__ == "__main__":
    main()
