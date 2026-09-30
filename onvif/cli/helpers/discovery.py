"""ONVIF discovery helpers."""

from datetime import datetime

from onvif.cli.utils import colorize
from onvif.utils import ONVIFDiscovery


def discover_devices(
    timeout: int = 4,
    interface: str | None = None,
    prefer_https: bool = False,
    filter_term: str | None = None,
) -> list:
    """Discover ONVIF devices on the network using WS-Discovery.

    Args:
        timeout (int): Discovery timeout in seconds
        interface (str | None): Network interface to use for discovery
        prefer_https (bool): If True, prioritize HTTPS XAddrs when available
        filter_term (str | None): Optional search term to filter devices by
            types or scopes (case-insensitive)

    Returns:
        List of discovered devices with connection info
    """
    # Use ONVIFDiscovery class
    discovery = ONVIFDiscovery(timeout=timeout, interface=interface)

    print(f"\n{colorize('Discovering ONVIF devices on network...', 'yellow')}")
    print(f"Network interface: {colorize(discovery.get_local_ip(), 'white')}")
    print(f"Timeout: {timeout}s")
    if filter_term:
        print(f"Filter: {colorize(filter_term, 'yellow')}")
    print()

    devices = discovery.discover(prefer_https=prefer_https, search=filter_term)

    return devices


def select_device_interactive(devices: list) -> tuple[str, int, bool] | None:
    """Display devices and allow user to select one interactively.

    Args:
        devices (list): Discovered devices

    Returns:
        Tuple of (host, port, use_https) or None if cancelled
    """
    if not devices:
        print(f"\n{colorize('No ONVIF devices found.', 'red')}")
        return None

    print(f"{colorize(f'Found {len(devices)} ONVIF device(s):', 'green')}")

    for idx, device in enumerate(devices, 1):
        protocol = "https" if device.get("use_https", False) else "http"
        host_port = f"{device['host']}:{device['port']}"
        protocol_indicator = (
            colorize("🔒 HTTPS", "green")
            if device.get("use_https", False)
            else colorize("HTTP", "white")
        )
        print(
            f"\n{colorize(f"[{idx}]", "yellow")} {colorize(host_port, 'yellow')} ({protocol_indicator})"
        )

        # Remove uuid: or urn:uuid: prefix from EPR
        epr_display = device["epr"]
        if epr_display.startswith("urn:uuid:"):
            epr_display = epr_display.replace("urn:uuid:", "")
        elif epr_display.startswith("uuid:"):
            epr_display = epr_display.replace("uuid:", "")
        print(f"    [uuid] {epr_display}")

        _print_optional_field("hostname", device.get("hostname"))

        _print_optional_field(
            "xaddrs",
            " ".join(f"[{xaddr}]" for xaddr in device.get("xaddrs", [])),
        )

        if device.get("date_time"):
            utc = (
                datetime.fromisoformat(device["date_time"].get("utc")).strftime(
                    "%H:%M:%S %d-%m-%Y"
                )
                if device["date_time"].get("utc")
                else ""
            )
            local = (
                datetime.fromisoformat(device["date_time"].get("local")).strftime(
                    "%H:%M:%S %d-%m-%Y"
                )
                if device["date_time"].get("local")
                else ""
            )
            print(
                f"    [date_time]"
                f'{" [UTC: " + utc + "]" if utc else ""}'
                f'{" [Local: " + local + "]" if local else ""}'
            )

        _print_optional_field(
            "types",
            " ".join(f"[{device_type}]" for device_type in device.get("types", [])),
        )

        _print_optional_field(
            "services",
            " ".join(f"[{service}]" for service in device.get("services", [])),
            "cyan",
        )

        if device.get("scopes"):
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

    return _process_device_selection(protocol, devices)


def _print_optional_field(
    label: str,
    value: object,
    color: str | None = None,
) -> None:
    """Print an optional device field when it has a value."""
    if not value:
        return

    if color:
        value = colorize(str(value), color)

    print(f"    [{label}] {value}")


def _process_device_selection(protocol, devices):
    """Simple selection (without arrow keys for cross-platform compatibility)"""
    while True:
        try:
            selection = input(
                f"\nSelect device number {colorize(f'1-{len(devices)}', 'white')} "
                f"or {colorize('q', 'white')} to quit: "
            )

            if selection.lower() == "q":
                return None

            idx = int(selection)
            if 1 <= idx <= len(devices):
                selected = devices[idx - 1]
                protocol = "https" if selected.get("use_https", False) else "http"
                host_port = f"{selected['host']}:{selected['port']}"
                print(
                    f"\n{colorize('Selected:', 'green')} {colorize(protocol, 'cyan')}:"
                    f"//{colorize(host_port, 'yellow')}"
                )

                return (
                    selected["host"],
                    selected["port"],
                    selected.get("use_https", False),
                )

            print(colorize("Invalid selection. Please try again.", "red"))

        except ValueError:
            print(colorize("Invalid input. Please enter a number.", "red"))
        except (EOFError, KeyboardInterrupt):
            return None
