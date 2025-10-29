"""
Path: examples/logger.py
Author: @kaburagisec
Created: October 29, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

Applied for (>= v0.2.0 patch)

This script demonstrates the comprehensive logging functionality implemented
across the ONVIF Python library. It shows how to configure different logging
levels and capture detailed information about ONVIF operations.

Usage:
    python logger.py [device_ip] [username] [password] [options]

Example:
    python logger.py 192.168.1.17 admin admin123 --port 8000
    python logger.py --discover-only        # Just run discovery
    python logger.py --level DEBUG          # Will show all logs
    python logger.py --level WARNING        # Only warnings and errors
    python logger.py --level ERROR          # Only errors messages
    python logger.py --level INFO           # Only info, errors, warnings
"""

import sys
import logging
import argparse
from datetime import datetime
import os

from onvif import ONVIFClient, ONVIFDiscovery, ONVIFWSDL


def setup_logging(level=logging.INFO):
    """Configure logging with detailed formatting for ONVIF operations.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # File handler for detailed logging
    log_filename = (
        f"onvif_logging_example_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Configure ONVIF logger (this will handle all onvif.* loggers)
    onvif_logger = logging.getLogger("onvif")
    onvif_logger.setLevel(level)
    onvif_logger.addHandler(console_handler)
    onvif_logger.addHandler(file_handler)

    # Suppress verbose logging from external libraries
    for logger_name in ["zeep", "urllib3", "requests"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    print(
        f"Logging configured - Level: {logging.getLevelName(level)}, File: {log_filename}"
    )
    return log_filename


def demonstrate_discovery_logging():
    """Demonstrate ONVIF device discovery with detailed logging."""
    print("\n" + "=" * 60)
    print("ONVIF DEVICE DISCOVERY LOGGING DEMONSTRATION")
    print("=" * 60)

    # Create discovery instance with logging
    discovery = ONVIFDiscovery(timeout=5)

    print("\n1. Starting device discovery...")
    devices = discovery.discover(prefer_https=True, search=None)

    print(f"\n2. Discovery Results:")
    if devices:
        for i, device in enumerate(devices, 1):
            print(f"   Device {i}:")
            print(f"     Host: {device['host']}")
            print(f"     Port: {device['port']}")
            print(f"     Endpoint: {device['host']}:{device['port']}")
            print(f"     HTTPS: {device['use_https']}")
            print(f"     Types: {', '.join(device.get('types', []))}")
            print(
                f"     Scopes: {', '.join(device.get('scopes', [])[:2])}..."
            )  # First 2 scopes
    else:
        print("   No devices found")

    return devices


def demonstrate_wsdl_logging():
    """Demonstrate WSDL resolution and management logging."""
    print("\n" + "=" * 60)
    print("WSDL RESOLUTION LOGGING DEMONSTRATION")
    print("=" * 60)

    print("\n1. Getting WSDL definitions...")

    # Test various WSDL services
    services_to_test = [
        ("devicemgmt", "ver10"),
        ("media", "ver20"),  # This will raise ERROR log (wrong version for testing)
        ("ptz", "ver20"),
        ("imaging", "ver20"),
        ("events", "ver10"),
    ]

    for service, version in services_to_test:
        try:
            definition = ONVIFWSDL.get_definition(service, version)
            print(f"   ✓ {service} ({version}): {os.path.basename(definition['path'])}")
        except Exception as e:
            print(f"   ✗ {service} ({version}): {e}")

    # Show custom WSDL directory functionality
    print(
        f"\n2. Current WSDL directory: {ONVIFWSDL.get_custom_wsdl_dir() or 'Built-in'}"
    )


def demonstrate_client_logging(host, port, username, password):
    """Demonstrate ONVIF client operations with comprehensive logging."""
    print("\n" + "=" * 60)
    print("ONVIF CLIENT OPERATIONS LOGGING DEMONSTRATION")
    print("=" * 60)

    print(f"\n1. Connecting to ONVIF device: {host}:{port}")

    # Create client with XML capture for detailed SOAP logging
    client = ONVIFClient(
        host=host,
        port=port,
        username=username,
        password=password,
        timeout=10,
        capture_xml=True,  # Enable XML capture
        use_https=False,
        verify_ssl=True,
    )

    print("\n2. Accessing Device Management service...")
    try:
        device = client.devicemgmt()
        print("   ✓ Device Management service initialized")

        # Test basic device operations
        print("\n3. Getting device information...")
        device_info = device.GetDeviceInformation()
        print(f"   ✓ Device: {device_info.Manufacturer} {device_info.Model}")
        print(f"   ✓ Firmware: {device_info.FirmwareVersion}")
        print(f"   ✓ Serial: {device_info.SerialNumber}")

    except Exception as e:
        print(f"   ✗ Device Management failed: {e}")
        return None

    print("\n4. Testing service capabilities...")

    # Test various services with error handling
    services_to_test = [
        ("media", "GetProfiles"),
        ("ptz", "GetConfigurations"),
        ("imaging", "GetImagingSettings"),
        ("events", "GetEventProperties"),
    ]

    for service_name, operation in services_to_test:
        try:
            print(f"   Testing {service_name}.{operation}...")
            service = getattr(client, service_name)()
            method = getattr(service, operation)
            result = method()
            print(f"   ✓ {service_name}.{operation} succeeded")
        except Exception as e:
            print(f"   ✗ {service_name}.{operation} failed: {type(e).__name__}")

    print("\n5. Testing type creation...")
    try:
        # Test type creation with logging
        hostname_type = device.type("SetHostname")
        print("   ✓ SetHostname type created successfully")

        user_type = device.type("CreateUsers")
        print("   ✓ CreateUsers type created successfully")

    except Exception as e:
        print(f"   ✗ Type creation failed: {e}")

    # Show XML capture results if available
    if hasattr(client, "xml_plugin") and client.xml_plugin:
        print(f"\n6. XML Capture Summary:")
        history = client.xml_plugin.get_history()
        print(f"   Total SOAP transactions: {len(history)}")

        if history:
            last_request = client.xml_plugin.get_last_request()
            last_response = client.xml_plugin.get_last_response()
            print(
                f"   Last request size: {len(last_request) if last_request else 0} chars"
            )
            print(
                f"   Last response size: {len(last_response) if last_response else 0} chars"
            )

    return client


def demonstrate_error_handling_logging():
    """Demonstrate error handling and exception logging."""
    print("\n" + "=" * 60)
    print("ERROR HANDLING LOGGING DEMONSTRATION")
    print("=" * 60)

    print("\n1. Testing connection to non-existent device...")
    try:
        # This should fail and demonstrate error logging
        fake_client = ONVIFClient(
            host="192.168.999.999", port=80, username="fake", password="fake", timeout=3
        )
        device = fake_client.devicemgmt()
        device.GetDeviceInformation()
    except Exception as e:
        print(f"   ✓ Expected error logged: {type(e).__name__}")

    print("\n2. Testing invalid service operations...")
    # Additional error scenarios could be added here
    print("   ✓ Error handling demonstration complete")


def main():
    """Main demonstration function with command line argument handling."""
    parser = argparse.ArgumentParser(
        description="ONVIF Library Logging Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument("host", nargs="?", default=None, help="ONVIF device IP address")
    parser.add_argument(
        "username", nargs="?", default="admin", help="ONVIF username (default: admin)"
    )
    parser.add_argument(
        "password", nargs="?", default="admin", help="ONVIF password (default: admin)"
    )
    parser.add_argument(
        "--port", type=int, default=80, help="ONVIF device port (default: 80)"
    )
    parser.add_argument(
        "--level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--discover-only", action="store_true", help="Only run device discovery"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = getattr(logging, args.level.upper())
    log_file = setup_logging(log_level)

    print("ONVIF Python Library - Comprehensive Logging Example")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Log Level: {log_level}")

    try:
        # Always demonstrate discovery
        devices = demonstrate_discovery_logging()

        # Always demonstrate WSDL logging
        demonstrate_wsdl_logging()

        if not args.discover_only:
            # Determine device to connect to
            if args.host:
                host = args.host
                port = args.port
            elif devices:
                # Use first discovered device
                device = devices[0]
                host = device["host"]
                port = device["port"]
                print(f"\nUsing discovered device: {host}:{port}")
            else:
                print(
                    "\nNo device specified and none discovered. Use --discover-only or provide device details."
                )
                return

            # Demonstrate client operations
            client = demonstrate_client_logging(
                host, port, args.username, args.password
            )

            # Demonstrate error handling
            demonstrate_error_handling_logging()

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.exception("Unexpected error in main demonstration")

    finally:
        print("\n" + "=" * 60)
        print("LOGGING DEMONSTRATION COMPLETE")
        print("=" * 60)
        print(f"\nDetailed logs saved to: {log_file}")
        print("\nLog file contains:")
        print("- Complete ONVIF operation traces")
        print("- Debug information (ONVIF-specific)")
        print("- Error details and stack traces")
        print("- Network communication logs (ONVIF-focused)")
        print("- SOAP XML requests/responses (if XML capture enabled)")
        print("- Filtered output (excludes verbose Zeep/HTTP library logs)")

        # Show brief log file summary
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            debug_count = sum(1 for line in lines if " - DEBUG - " in line)
            info_count = sum(1 for line in lines if " - INFO - " in line)
            warning_count = sum(1 for line in lines if " - WARNING - " in line)
            error_count = sum(1 for line in lines if " - ERROR - " in line)

            print(f"\nLog Summary: {len(lines)} total lines")
            print(
                f"  DEBUG: {debug_count}, INFO: {info_count}, WARNING: {warning_count}, ERROR: {error_count}"
            )

        except Exception:
            pass


if __name__ == "__main__":
    main()
