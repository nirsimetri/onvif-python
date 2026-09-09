"""Utility functions for ONVIF CLI tools."""

from __future__ import annotations

import ctypes
import json
import os
import re
from ctypes import wintypes
from functools import lru_cache
from typing import Any

# ONVIF namespace to service name mapping (used globally)
# Format: namespace -> list of (service_name, binding_pattern)
# binding_pattern is used to identify specific binding in multi-binding services
ONVIF_NAMESPACE_MAP = {
    "http://www.onvif.org/ver10/device/wsdl": [("devicemgmt", "DeviceBinding")],
    "http://www.onvif.org/ver10/events/wsdl": [
        ("events", "EventBinding"),
        ("pullpoint", "PullPointSubscriptionBinding"),
        ("notification", "NotificationProducerBinding"),
        ("subscription", "SubscriptionManagerBinding"),
    ],
    "http://www.onvif.org/ver20/imaging/wsdl": [("imaging", "ImagingBinding")],
    "http://www.onvif.org/ver10/media/wsdl": [("media", "MediaBinding")],
    "http://www.onvif.org/ver20/media/wsdl": [("media2", "Media2Binding")],
    "http://www.onvif.org/ver20/ptz/wsdl": [("ptz", "PTZBinding")],
    "http://www.onvif.org/ver10/deviceIO/wsdl": [("deviceio", "DeviceIOBinding")],
    "http://www.onvif.org/ver10/display/wsdl": [("display", "DisplayBinding")],
    "http://www.onvif.org/ver20/analytics/wsdl": [
        ("analytics", "AnalyticsEngineBinding"),
        ("ruleengine", "RuleEngineBinding"),
    ],
    "http://www.onvif.org/ver10/analyticsdevice/wsdl": [
        ("analyticsdevice", "AnalyticsDeviceBinding")
    ],
    "http://www.onvif.org/ver10/accesscontrol/wsdl": [("accesscontrol", "PACSBinding")],
    "http://www.onvif.org/ver10/doorcontrol/wsdl": [
        ("doorcontrol", "DoorControlBinding")
    ],
    "http://www.onvif.org/ver10/accessrules/wsdl": [
        ("accessrules", "AccessRulesBinding")
    ],
    "http://www.onvif.org/ver10/actionengine/wsdl": [
        ("actionengine", "ActionEngineBinding")
    ],
    "http://www.onvif.org/ver10/provisioning/wsdl": [
        ("provisioning", "ProvisioningBinding")
    ],
    "http://www.onvif.org/ver10/receiver/wsdl": [("receiver", "ReceiverBinding")],
    "http://www.onvif.org/ver10/recording/wsdl": [("recording", "RecordingBinding")],
    "http://www.onvif.org/ver10/replay/wsdl": [("replay", "ReplayBinding")],
    "http://www.onvif.org/ver10/schedule/wsdl": [("schedule", "ScheduleBinding")],
    "http://www.onvif.org/ver10/search/wsdl": [("search", "SearchBinding")],
    "http://www.onvif.org/ver10/thermal/wsdl": [("thermal", "ThermalBinding")],
    "http://www.onvif.org/ver10/uplink/wsdl": [("uplink", "UplinkBinding")],
    "http://www.onvif.org/ver10/appmgmt/wsdl": [("appmgmt", "AppManagementBinding")],
    "http://www.onvif.org/ver10/authenticationbehavior/wsdl": [
        ("authenticationbehavior", "AuthenticationBehaviorBinding")
    ],
    "http://www.onvif.org/ver10/credential/wsdl": [("credential", "CredentialBinding")],
    "http://www.onvif.org/ver10/advancedsecurity/wsdl": [
        ("advancedsecurity", "AdvancedSecurityServiceBinding"),
        ("jwt", "JWTBinding"),
        ("keystore", "KeystoreBinding"),
        ("tlsserver", "TLSServerBinding"),
        ("dot1x", "Dot1XBinding"),
        ("authorizationserver", "AuthorizationServerBinding"),
        ("mediasigning", "MediaSigningBinding"),
    ],
}


def _is_valid_json(s: str) -> bool:
    """Check if a string is valid JSON without raising exceptions."""
    try:
        json.loads(s)
    except ValueError:
        return False
    return True


def parse_json_params(params_str: str) -> dict[str, Any]:
    """Parse parameters from a JSON string or key=value pairs into a dict.

    Supports:
      - JSON: '{"a": 1, "b": 2}'
      - key=value key2=value2 ... (space/comma separated, supports quoted values)
    """
    params_str = params_str.strip()
    if not params_str:
        return {}

    # If the whole string is valid JSON, return it directly
    if _is_valid_json(params_str):
        return json.loads(params_str)  # We know it's valid, so this should not fail

    # Otherwise parse key=value pairs but allow JSON values for the right-hand side
    # We split tokens while respecting quoted strings using shlex, but must not
    # break JSON objects/arrays that contain spaces or commas. To do that we
    # first find top-level separators (spaces or commas) that are not inside
    # quotes or brackets.

    def split_top_level(s: str):
        tokens: list[str] = []
        buf: list[str] = []
        depth = 0
        in_single = False
        in_double = False
        for ch in s:
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif not in_single and not in_double:
                if ch in "{[(":
                    depth += 1
                elif ch in "}])":
                    depth = max(0, depth - 1)

            if depth == 0 and not in_single and not in_double and ch in [",", " "]:
                # treat as separator only when buffer has content
                if buf:
                    token = "".join(buf).strip()
                    if token:
                        tokens.append(token)
                    buf = []
                # skip additional separators
                continue

            buf.append(ch)

        if buf:
            token = "".join(buf).strip()
            if token:
                tokens.append(token)

        return tokens

    params: dict[str, Any] = {}
    tokens: list[str] = split_top_level(params_str)

    for pair in tokens:
        if "=" in pair:
            key, value = pair.split("=", 1)
            key = key.strip().strip("\"'")
            v_raw = value.strip()

            # Try to parse the RHS as JSON first (to support nested objects/arrays)
            try:
                v = json.loads(v_raw)
            except (AttributeError, ValueError, TypeError):
                # If it fails, it might be a quoted JSON string. Try unquoting it once.
                v_token = v_raw
                if (v_token.startswith("'") and v_token.endswith("'")) or (
                    v_token.startswith('"') and v_token.endswith('"')
                ):
                    v_token = v_token[1:-1]

                # Try parsing as JSON again
                try:
                    v = json.loads(v_token)
                except (AttributeError, ValueError, TypeError):
                    # If it still fails, the shell might have stripped quotes from keys.
                    # Let's try to fix it by adding quotes around keys.
                    try:
                        # This regex finds keys (words followed by a colon) and adds quotes
                        fixed_json_str = re.sub(
                            r"([{\s,])([a-zA-Z0-9_]+)\s*:", r'\1"\2":', v_token
                        )
                        v = json.loads(fixed_json_str)
                    except (AttributeError, ValueError, TypeError):
                        # If it's still not JSON, fall back to simple type interpretation
                        if isinstance(v_token, str) and v_token.lower() == "true":
                            v = True
                        elif isinstance(v_token, str) and v_token.lower() == "false":
                            v = False
                        elif isinstance(v_token, str) and v_token.lower() in (
                            "none",
                            "null",
                        ):
                            v = None
                        else:
                            # Try numeric conversion
                            try:
                                if isinstance(v_token, str) and "." in v_token:
                                    v = float(v_token)
                                else:
                                    v = int(v_token)
                            except (AttributeError, ValueError, TypeError):
                                v = v_token  # It's just a string

            params[key] = v

    return params


def get_service_required_args(service_name: str) -> list[str] | None:
    """Get required arguments for services that need them.

    Returns list of required argument names, or None if service doesn't need args.
        Services that require arguments:
        - pullpoint, subscription: requires SubscriptionRef
    """
    if service_name in ["pullpoint", "subscription"]:
        return ["SubscriptionRef"]
    return None


def get_service_methods(service_obj) -> list:
    """Get list of available methods for a service."""
    methods = []
    for attr_name in dir(service_obj):
        if (
            not attr_name.startswith("_")
            and callable(getattr(service_obj, attr_name))
            and attr_name not in ["type", "desc", "operations", "to_dict"]
        ):
            # Skip helper methods
            methods.append(attr_name)
    return sorted(methods)


@lru_cache(maxsize=1)
def _colors_enabled() -> bool:
    """Check whether ANSI colors are supported by the terminal."""
    if os.name != "nt":
        return True

    try:
        # Enable ANSI escape sequences
        kernel32 = ctypes.windll.kernel32
        h_stdout = kernel32.GetStdHandle(-11)

        # Get current console mode
        mode = wintypes.DWORD()
        kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode))

        enable_virtual_terminal_processing = 0x0004
        return bool(
            kernel32.SetConsoleMode(
                h_stdout,
                mode.value | enable_virtual_terminal_processing,
            )
        )
    except (ImportError, AttributeError, OSError):
        return False


def colorize(text: str, color: str) -> str:
    """Add color to text for terminal output."""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m",
    }

    if not _colors_enabled():
        return text

    return f"{colors.get(color, '')}{text}{colors['reset']}"


def format_capabilities_as_services(capabilities) -> str:
    """Format capabilities response as service list with XAddr."""
    services = []

    # Map of capability names to service function names
    service_map = {
        "Device": "devicemgmt",
        "Analytics": "analytics",
        "Events": "events",
        "Imaging": "imaging",
        "Media": "media",
        "PTZ": "ptz",
        "Extension": None,  # Handle extensions separately
    }

    for cap_name, service_func in service_map.items():
        if service_func and hasattr(capabilities, cap_name):
            cap = getattr(capabilities, cap_name)
            if cap and "XAddr" in cap:
                services.append(f"  {colorize(service_func, 'yellow')}")
                services.append(f"    {colorize('XAddr:', 'white')} {cap['XAddr']}")

    # Handle extensions
    if hasattr(capabilities, "Extension") and capabilities.Extension:
        ext = capabilities.Extension
        ext_services = {
            # first-level extension capabilities
            "DeviceIO": "deviceio",
            "Display": "display",
            "Recording": "recording",
            "Search": "search",
            "Replay": "replay",
            "Receiver": "receiver",
            "AnalyticsDevice": "analyticsdevice",
            # second-level extension capabilities
            "AccessControl": "accesscontrol",
            "DoorControl": "doorcontrol",
            "AccessRules": "accessrules",
            "ActionEngine": "actionengine",
            "AppManagement": "appmgmt",
            "AuthenticationBehavior": "authenticationbehavior",
            "Credential": "credential",
            "Provisioning": "provisioning",
            "Schedule": "schedule",
            "Thermal": "thermal",
            "Uplink": "uplink",
            "Security": "advancedsecurity",
        }

        for ext_name, service_func in ext_services.items():
            if hasattr(ext, ext_name):
                ext_service = getattr(ext, ext_name)
                if ext_service and "XAddr" in ext_service:
                    services.append(f"  {colorize(service_func, 'yellow')}")
                    services.append(
                        f"    {colorize('XAddr:', 'white')} {ext_service['XAddr']}"
                    )

        # Handle nested extensions
        if hasattr(ext, "Extensions") and ext.Extensions:
            ext_ext = ext.Extensions
            for ext_name, service_func in ext_services.items():
                if hasattr(ext_ext, ext_name):
                    ext_service = getattr(ext_ext, ext_name)
                    if ext_service and "XAddr" in ext_service:
                        services.append(f"  {colorize(service_func, 'yellow')}")
                        services.append(
                            f"    {colorize('XAddr:', 'white')} {ext_service['XAddr']}"
                        )

    if services:
        header = f"{colorize('Available Capabilities:', 'green')}"
        service_lines = "\n".join(services)
        result = f"{header}\n{service_lines}"
        return result

    return f"{colorize('No services found in capabilities', 'yellow')}"


def format_services_list(services_list) -> str:
    """Format GetServices response as service list with XAddr and binding support.

    Shows binding information for all services (single and multi-binding).
    """
    if not services_list:
        return f"{colorize('No services available', 'yellow')}"

    services = []
    header = f"{colorize('Available Services:', 'green')}"

    for service in services_list:
        namespace = getattr(service, "Namespace", "")
        xaddr = getattr(service, "XAddr", "")
        version = getattr(service, "Version", {})

        # Get service mappings for this namespace
        service_mappings = ONVIF_NAMESPACE_MAP.get(namespace, [])

        if not service_mappings:
            # Unknown namespace
            services.append(f"  {colorize(f'unknown({namespace})', 'yellow')}")
            services.append(f"    {colorize('XAddr    :', 'white')} {xaddr}")
            services.append(f"    {colorize('Namespace:', 'white')} {namespace}")
        else:
            # Add the main service entry (first service in mappings)
            main_service = service_mappings[0][0]
            services.append(f"  {colorize(main_service, 'cyan')}")
            services.append(f"    {colorize('XAddr    :', 'white')} {xaddr}")
            services.append(f"    {colorize('Namespace:', 'white')} {namespace}")

            # Always show binding information for all services
            if len(service_mappings) == 1:
                # Single binding - still show it
                service_name, binding = service_mappings[0]
                services.append(f"    {colorize('Binding  :', 'white')} {binding}")
            else:
                # Multi-binding - show all bindings (no filtering)
                # Always display all bindings for multi-binding services
                services.append(f"    {colorize('Bindings :', 'white')}")
                for service_name, binding in service_mappings:
                    services.append(
                        f"      - {colorize(service_name, 'green')} ({binding})"
                    )

        # Add version info
        if version:
            major = getattr(version, "Major", "")
            minor = getattr(version, "Minor", "")
            if major and minor:
                services.append(
                    f"    {colorize('Version  :', 'white')} {major}.{minor}"
                )
            elif major:
                services.append(f"    {colorize('Version  :', 'white')} {major}")

    service_lines = "\n".join(services)
    result = f"{header}\n{service_lines}"
    return result


def get_device_available_services(client) -> list:
    """Get list of services actually available on the connected device.

    For multi-binding services, returns all available service names.
    """
    available_services = ["devicemgmt"]  # devicemgmt is always available

    # Check if device has services information
    if hasattr(client, "services") and client.services:
        for service in client.services:
            namespace = getattr(service, "Namespace", None)
            if namespace and namespace in ONVIF_NAMESPACE_MAP:
                # Get all service names for this namespace (handles multi-binding)
                service_mappings = ONVIF_NAMESPACE_MAP[namespace]
                for service_name, _ in service_mappings:
                    if service_name not in available_services:
                        available_services.append(service_name)

    # Check capabilities as fallback
    elif hasattr(client, "capabilities") and client.capabilities:
        caps = client.capabilities

        # Check various capability attributes for service availability
        if hasattr(caps, "Analytics") and caps.Analytics:
            available_services.extend(["analytics", "ruleengine"])
        if hasattr(caps, "Events") and caps.Events:
            # Events namespace has multiple bindings
            available_services.extend(
                ["events", "pullpoint", "notification", "subscription"]
            )
        if hasattr(caps, "Imaging") and caps.Imaging:
            available_services.append("imaging")
        if hasattr(caps, "Media") and caps.Media:
            available_services.append("media")
        if hasattr(caps, "PTZ") and caps.PTZ:
            available_services.append("ptz")

        # Check for services in Extension (first level)
        if hasattr(caps, "Extension") and caps.Extension:
            ext = caps.Extension

            if hasattr(ext, "DeviceIO") and ext.DeviceIO:
                available_services.append("deviceio")
            if hasattr(ext, "Display") and ext.Display:
                available_services.append("display")
            if hasattr(ext, "Recording") and ext.Recording:
                available_services.append("recording")
            if hasattr(ext, "Search") and ext.Search:
                available_services.append("search")
            if hasattr(ext, "Replay") and ext.Replay:
                available_services.append("replay")
            if hasattr(ext, "Receiver") and ext.Receiver:
                available_services.append("receiver")
            if hasattr(ext, "AnalyticsDevice") and ext.AnalyticsDevice:
                available_services.append("analyticsdevice")

            # Check for nested Extension (second level)
            if hasattr(ext, "Extensions") and ext.Extensions:
                ext_ext = ext.Extensions

                if hasattr(ext_ext, "AccessControl") and ext_ext.AccessControl:
                    available_services.append("accesscontrol")
                if hasattr(ext_ext, "DoorControl") and ext_ext.DoorControl:
                    available_services.append("doorcontrol")
                if hasattr(ext_ext, "AccessRules") and ext_ext.AccessRules:
                    available_services.append("accessrules")
                if hasattr(ext_ext, "ActionEngine") and ext_ext.ActionEngine:
                    available_services.append("actionengine")
                if hasattr(ext_ext, "AppManagement") and ext_ext.AppManagement:
                    available_services.append("appmgmt")
                if (
                    hasattr(ext_ext, "AuthenticationBehavior")
                    and ext_ext.AuthenticationBehavior
                ):
                    available_services.append("authenticationbehavior")
                if hasattr(ext_ext, "Credential") and ext_ext.Credential:
                    available_services.append("credential")
                if hasattr(ext_ext, "Provisioning") and ext_ext.Provisioning:
                    available_services.append("provisioning")
                if hasattr(ext_ext, "Schedule") and ext_ext.Schedule:
                    available_services.append("schedule")
                if hasattr(ext_ext, "Thermal") and ext_ext.Thermal:
                    available_services.append("thermal")
                if hasattr(ext_ext, "Uplink") and ext_ext.Uplink:
                    available_services.append("uplink")
                if hasattr(ext_ext, "Security") and ext_ext.Security:
                    # Security namespace has multiple bindings
                    available_services.extend(
                        [
                            "security",
                            "jwt",
                            "keystore",
                            "tlsserver",
                            "dot1x",
                            "authorizationserver",
                            "mediasigning",
                        ]
                    )

    return sorted(set(available_services))  # Remove duplicates and sort
