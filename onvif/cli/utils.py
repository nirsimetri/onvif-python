# onvif/cli/utils.py

import json
import os
import inspect
from typing import Any, Dict, Optional
from lxml import etree
import re


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


def parse_json_params(params_str: str) -> Dict[str, Any]:
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
        tokens = []
        buf = []
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

    params = {}
    tokens = split_top_level(params_str)

    for pair in tokens:
        if "=" in pair:
            key, value = pair.split("=", 1)
            key = key.strip().strip("\"'")
            v_raw = value.strip()

            # Try to parse the RHS as JSON first (to support nested objects/arrays)
            try:
                v = json.loads(v_raw)
            except Exception:
                # If it fails, it might be a quoted JSON string. Try unquoting it once.
                v_token = v_raw
                if (v_token.startswith("'") and v_token.endswith("'")) or (
                    v_token.startswith('"') and v_token.endswith('"')
                ):
                    v_token = v_token[1:-1]

                # Try parsing as JSON again
                try:
                    v = json.loads(v_token)
                except Exception:
                    # If it still fails, the shell might have stripped quotes from keys.
                    # Let's try to fix it by adding quotes around keys.
                    try:
                        # This regex finds keys (words followed by a colon) and adds quotes
                        fixed_json_str = re.sub(
                            r"([{\s,])([a-zA-Z0-9_]+)\s*:", r'\1"\2":', v_token
                        )
                        v = json.loads(fixed_json_str)
                    except Exception:
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
                            except Exception:
                                v = v_token  # It's just a string

            params[key] = v

    return params


def get_service_required_args(service_name: str) -> Optional[list]:
    """
    Get required arguments for services that need them.
    Returns list of required argument names, or None if service doesn't need args.

    Services that require arguments:
    - pullpoint, subscription: requires SubscriptionRef
    - jwt, keystore, tlsserver, dot1x, authorizationserver, mediasigning: require xaddr
    """
    if service_name in ["pullpoint", "subscription"]:
        return ["SubscriptionRef"]
    elif service_name in [
        "jwt",
        "keystore",
        "tlsserver",
        "dot1x",
        "authorizationserver",
        "mediasigning",
    ]:
        return ["xaddr"]
    return None


def get_service_methods(service_obj) -> list:
    """Get list of available methods for a service"""
    methods = []
    for attr_name in dir(service_obj):
        if not attr_name.startswith("_") and callable(getattr(service_obj, attr_name)):
            # Skip helper methods
            if attr_name not in ["type", "desc", "operations"]:
                methods.append(attr_name)
    return sorted(methods)


def get_method_documentation(service_obj, method_name: str) -> Optional[Dict[str, Any]]:
    """
    Extracts documentation from WSDL and parameters from the Python method signature.
    Returns a dictionary with 'doc', 'required', and 'optional' keys.
    """
    doc_text = "No documentation available."
    required_args = []
    optional_args = []

    try:
        # 1. Get documentation from WSDL (existing logic)
        wsdl_path = service_obj.operator.wsdl_path

        # Use secure lxml parser
        parser = etree.XMLParser(
            resolve_entities=False,
            no_network=True,
            remove_blank_text=True,
        )
        tree = etree.parse(wsdl_path, parser)
        root = tree.getroot()
        namespaces = {
            node[0]: node[1] for node in etree.iterparse(wsdl_path, events=["start-ns"])
        }
        namespaces["wsdl"] = "http://schemas.xmlsoap.org/wsdl/"
        namespaces["xs"] = "http://www.w3.org/2001/XMLSchema"

        # Find the operation
        operation = root.find(f".//wsdl:operation[@name='{method_name}']", namespaces)
        if operation is None:
            return None

        # 1. Get documentation
        doc_element = operation.find("wsdl:documentation", namespaces)
        if doc_element is not None:
            # Handle mixed content (text and tags like <br/>, <ul>, <li>)
            text_parts = []
            if doc_element.text:
                text_parts.append(doc_element.text)

            for child in doc_element:
                if child.tag.endswith("ul") or child.tag.endswith("ol"):
                    text_parts.append("\n")
                    if child.text:
                        text_parts.append(child.text.strip())
                    for i, li in enumerate(child):
                        if li.tag.endswith("li"):
                            # Join all text within the <li> tag, then strip and prepend '- '
                            li_text = (
                                ("".join(li.itertext()))
                                .strip()
                                .replace("\n", " ")
                                .replace("\r", "")
                            )
                            li_text = " ".join(li_text.split())
                            text_parts.append(
                                f"\n  - {i+1}. {li_text}"
                                if child.tag.endswith("ol")
                                else f"\n  - {li_text}"
                            )
                    if child.tail:
                        if not child.tag.endswith("ol"):
                            text_parts.append("\n\n")  # Add paragraph break after list
                        text_parts.append(child.tail)
                elif child.tag.endswith("br"):
                    text_parts.append("\n\n")  # Paragraph break
                    if child.tail:
                        text_parts.append(child.tail)
                else:  # Other tags, just get text
                    if child.text:
                        text_parts.append(child.text)
                    if child.tail:
                        text_parts.append(child.tail)

            # Join all parts into a single string
            full_text = "".join(text_parts)

            # Normalize whitespace while preserving paragraph and list structures
            paragraphs = full_text.split("\n\n")
            cleaned_paragraphs = []
            for para in paragraphs:
                # Check if the paragraph is a list
                if "- " in para:
                    list_lines = para.strip().split("\n")
                    cleaned_list_lines = [
                        " ".join(line.split()) for line in list_lines if line.strip()
                    ]
                    cleaned_paragraphs.append("\n".join(cleaned_list_lines))
                else:
                    # It's a normal paragraph, collapse all whitespace
                    cleaned_para = " ".join(para.split())
                    cleaned_paragraphs.append(cleaned_para)

            doc_text = "\n\n".join(cleaned_paragraphs)
        else:
            doc_text = colorize("No description available.", "reset")

        # 2. Get parameters from Python method signature using inspect
        # Use object.__getattribute__ to bypass ONVIFService wrapper and get original method
        method = object.__getattribute__(service_obj, method_name)
        sig = inspect.signature(method)
        for param in sig.parameters.values():
            if param.name != "self":
                if param.default is inspect.Parameter.empty:
                    required_args.append(param.name)
                else:
                    optional_args.append(param.name)

        return {"doc": doc_text, "required": required_args, "optional": optional_args}

    except (etree.ParseError, FileNotFoundError, AttributeError, ValueError):
        # Fallback in case of any error, still try to get params
        try:
            # Use object.__getattribute__ to bypass ONVIFService wrapper and get original method
            method = object.__getattribute__(service_obj, method_name)
            sig = inspect.signature(method)
            for param in sig.parameters.values():
                if param.name != "self":
                    if param.default is inspect.Parameter.empty:
                        required_args.append(param.name)
                    else:
                        optional_args.append(param.name)
            return {
                "doc": doc_text,
                "required": required_args,
                "optional": optional_args,
            }
        except (AttributeError, ValueError):
            return None
    except Exception:
        return None


def colorize(text: str, color: str) -> str:
    """Add color to text for terminal output"""
    # Enable ANSI colors on Windows
    if not hasattr(colorize, "_colors_enabled"):
        colorize._colors_enabled = True
        if os.name == "nt":  # Windows
            try:
                import ctypes
                from ctypes import wintypes

                # Enable ANSI escape sequences
                kernel32 = ctypes.windll.kernel32
                h_stdout = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE

                # Get current console mode
                mode = wintypes.DWORD()
                kernel32.GetConsoleMode(h_stdout, ctypes.byref(mode))

                # Enable virtual terminal processing
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                kernel32.SetConsoleMode(
                    h_stdout, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
                )
            except (ImportError, AttributeError, OSError):
                # Specific exceptions that can occur:
                # - ImportError: ctypes not available
                # - AttributeError: Windows API functions not available
                # - OSError: Console mode setting failed
                colorize._colors_enabled = False

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

    return f"{colors.get(color, '')}{text}{colors['reset']}"


def format_capabilities_as_services(capabilities) -> str:
    """Format capabilities response as service list with XAddr"""
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
    else:
        return f"{colorize('No services found in capabilities', 'yellow')}"


def format_services_list(services_list) -> str:
    """Format GetServices response as service list with XAddr and binding support.
    Shows binding information for all services (single and multi-binding)."""
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
            services.append(f"    {colorize('XAddr   :', 'white')} {xaddr}")
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
    For multi-binding services, returns all available service names."""
    available_services = ["devicemgmt"]  # devicemgmt is always available

    # Check if device has services information
    if hasattr(client, "services") and client.services:
        for service in client.services:
            namespace = getattr(service, "Namespace", None)
            if namespace and namespace in ONVIF_NAMESPACE_MAP:
                # Get all service names for this namespace (handles multi-binding)
                service_mappings = ONVIF_NAMESPACE_MAP[namespace]
                for service_name, binding in service_mappings:
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

    # Additional check: Try to call security.GetServiceCapabilities() to verify availability
    # This is necessary because Security service might not be reported in GetServices/GetCapabilities
    # Use caching to avoid calling GetServiceCapabilities repeatedly
    if "security" not in available_services:
        # Check if we've already tried to get security capabilities
        if not hasattr(client, "_security_capabilities_checked"):
            client._security_capabilities_checked = False
            client._security_capabilities = None

        if not client._security_capabilities_checked:
            # First time check - call GetServiceCapabilities and cache result
            try:
                security_service = client.security()
                # Try to call GetServiceCapabilities to verify the service is actually available
                caps = security_service.GetServiceCapabilities()

                # Cache the capabilities for future use
                client._security_capabilities = caps
                client._security_capabilities_checked = True

            except Exception:
                # Security service not available, mark as checked
                client._security_capabilities_checked = True
                client._security_capabilities = None

        # Use cached capabilities
        if client._security_capabilities is not None:
            caps = client._security_capabilities

            # If successful, add main security service
            available_services.append("security")

            # Check each sub-service capability to determine availability
            # Only add sub-services if their corresponding capability is not None
            if (
                hasattr(caps, "KeystoreCapabilities")
                and caps.KeystoreCapabilities is not None
            ):
                available_services.append("keystore")

            if (
                hasattr(caps, "TLSServerCapabilities")
                and caps.TLSServerCapabilities is not None
            ):
                available_services.append("tlsserver")

            if (
                hasattr(caps, "Dot1XCapabilities")
                and caps.Dot1XCapabilities is not None
            ):
                available_services.append("dot1x")

            if (
                hasattr(caps, "AuthorizationServer")
                and caps.AuthorizationServer is not None
            ):
                available_services.append("authorizationserver")

            if hasattr(caps, "MediaSigning") and caps.MediaSigning is not None:
                available_services.append("mediasigning")

    # Additional check for JWT service: Try to call jwt.GetJWTConfiguration()
    # JWT doesn't have a capability in GetServiceCapabilities, so we need to test it directly
    if "jwt" not in available_services:
        # Check if we've already tried to get JWT availability
        if not hasattr(client, "_jwt_checked"):
            client._jwt_checked = False
            client._jwt_available = None

        if not client._jwt_checked:
            # First time check - try to call GetJWTConfiguration and cache result
            try:
                # JWT service requires xaddr from security service
                # Try to construct xaddr from security service endpoint
                protocol = "https" if client.common_args["use_https"] else "http"
                default_xaddr = f"{protocol}://{client.common_args['host']}:{client.common_args['port']}/onvif/AdvancedSecurity"

                # Try to call GetJWTConfiguration to verify JWT is available
                jwt_service = client.jwt(xaddr=default_xaddr)
                jwt_service.GetJWTConfiguration()

                # If successful, JWT is available
                client._jwt_available = True
                client._jwt_checked = True

            except Exception:
                # JWT service not available, mark as checked
                client._jwt_checked = True
                client._jwt_available = False

        # Use cached JWT availability
        if client._jwt_available:
            available_services.append("jwt")

    return sorted(list(set(available_services)))  # Remove duplicates and sort


def clean_documentation_html(doc_text: str) -> str:
    """
    Clean HTML tags from documentation text and convert links to readable format.

    Args:
        doc_text: Documentation text that may contain HTML tags

    Returns:
        Cleaned text with HTML tags removed and links converted
    """
    import re

    if not doc_text:
        return doc_text

    # Convert <a href="url">text</a> to "text (url)"
    # Use DOTALL flag to match across newlines
    def replace_link(match):
        url = match.group(1)
        text = match.group(2).strip()  # Strip whitespace from link text
        if text:
            return f"{text} ({url})"
        else:
            return url  # If no text, just return URL

    # Replace anchor tags - handle newlines and whitespace
    doc_text = re.sub(
        r'<a\s+href=["\']([^"\']+)["\']>(.*?)</a>',
        replace_link,
        doc_text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Remove any remaining HTML tags
    doc_text = re.sub(r"<[^>]+>", "", doc_text)

    # Clean up multiple spaces and newlines
    doc_text = re.sub(r"\s+", " ", doc_text)

    return doc_text.strip()


def extract_documentation_text(doc_elem) -> str:
    """
    Extract full text from xs:documentation element including child elements.
    This handles cases where documentation contains HTML tags like <a href="">.

    Args:
        doc_elem: The xs:documentation XML element

    Returns:
        Full text content including text from child elements
    """
    if doc_elem is None:
        return ""

    parts = []

    # Get text before first child
    if doc_elem.text:
        parts.append(doc_elem.text)

    # Get text from and after each child element
    for child in doc_elem:
        if child.text:
            parts.append(child.text)
        if child.tail:
            parts.append(child.tail)

    return "".join(parts)


def get_operation_type_info(
    service_obj, operation_name: str
) -> Optional[Dict[str, Any]]:
    """
    Extract input and output message types from WSDL for a given operation.
    Returns a dictionary with 'input' and 'output' keys containing message details.
    """
    try:
        wsdl_path = service_obj.operator.wsdl_path

        # Use secure lxml parser
        parser = etree.XMLParser(
            resolve_entities=False,
            no_network=True,
            remove_blank_text=True,
        )
        tree = etree.parse(wsdl_path, parser)
        root = tree.getroot()

        namespaces = {
            node[0]: node[1] for node in etree.iterparse(wsdl_path, events=["start-ns"])
        }
        namespaces["wsdl"] = "http://schemas.xmlsoap.org/wsdl/"
        namespaces["xs"] = "http://www.w3.org/2001/XMLSchema"

        # Build a schema context that includes all imported schemas
        schema_context = {
            "roots": [root],  # Start with WSDL root
            "namespaces": namespaces,
            "wsdl_dir": os.path.dirname(wsdl_path),
        }

        # Load all imported/included schemas
        _load_imported_schemas(root, schema_context, namespaces)

        # Find the operation in portType
        operation = root.find(
            f".//wsdl:portType/wsdl:operation[@name='{operation_name}']", namespaces
        )

        if operation is None:
            return None

        result = {"input": None, "output": None}

        # Get input message
        input_elem = operation.find("wsdl:input", namespaces)
        if input_elem is not None:
            input_msg_name = input_elem.get("message")
            if input_msg_name:
                # Remove namespace prefix
                input_msg_name = input_msg_name.split(":")[-1]
                result["input"] = parse_message_from_wsdl(
                    root, input_msg_name, namespaces, schema_context
                )

        # Get output message
        output_elem = operation.find("wsdl:output", namespaces)
        if output_elem is not None:
            output_msg_name = output_elem.get("message")
            if output_msg_name:
                # Remove namespace prefix
                output_msg_name = output_msg_name.split(":")[-1]
                result["output"] = parse_message_from_wsdl(
                    root, output_msg_name, namespaces, schema_context
                )

        return result

    except Exception:
        return None


def _load_imported_schemas(root, schema_context: dict, namespaces: dict):
    """
    Recursively load all imported and included schemas into the schema context.
    """

    # Find all xs:import and xs:include in xs:schema elements
    for schema in root.findall(".//xs:schema", namespaces):
        # Process imports
        for import_elem in schema.findall("xs:import", namespaces):
            schema_location = import_elem.get("schemaLocation")
            if schema_location and not schema_location.startswith("http"):
                # Resolve relative path
                schema_path = os.path.join(schema_context["wsdl_dir"], schema_location)
                schema_path = os.path.normpath(schema_path)

                if os.path.exists(schema_path):
                    try:
                        # Use secure parser for imported schemas
                        parser = etree.XMLParser(
                            resolve_entities=False,
                            no_network=True,
                            remove_blank_text=True,
                        )
                        imported_tree = etree.parse(schema_path, parser)
                        imported_root = imported_tree.getroot()

                        # Add to context if not already present
                        if imported_root not in schema_context["roots"]:
                            schema_context["roots"].append(imported_root)

                            # Recursively load schemas from this imported schema
                            _load_imported_schemas(
                                imported_root,
                                {
                                    "roots": schema_context["roots"],
                                    "namespaces": namespaces,
                                    "wsdl_dir": os.path.dirname(schema_path),
                                },
                                namespaces,
                            )
                    except (etree.XMLSyntaxError, OSError, PermissionError):
                        # Skip files that can't be parsed or accessed:
                        # - XMLSyntaxError: malformed XML
                        # - OSError: file access issues
                        # - PermissionError: insufficient permissions
                        continue

        # Process includes
        for include_elem in schema.findall("xs:include", namespaces):
            schema_location = include_elem.get("schemaLocation")
            if schema_location and not schema_location.startswith("http"):
                # Resolve relative path
                schema_path = os.path.join(schema_context["wsdl_dir"], schema_location)
                schema_path = os.path.normpath(schema_path)

                if os.path.exists(schema_path):
                    try:
                        # Use secure parser for included schemas
                        parser = etree.XMLParser(
                            resolve_entities=False,
                            no_network=True,
                            remove_blank_text=True,
                        )
                        included_tree = etree.parse(schema_path, parser)
                        included_root = included_tree.getroot()

                        # Add to context if not already present
                        if included_root not in schema_context["roots"]:
                            schema_context["roots"].append(included_root)

                            # Recursively load schemas from this included schema
                            _load_imported_schemas(
                                included_root,
                                {
                                    "roots": schema_context["roots"],
                                    "namespaces": namespaces,
                                    "wsdl_dir": os.path.dirname(schema_path),
                                },
                                namespaces,
                            )
                    except (etree.XMLSyntaxError, OSError, PermissionError):
                        # Skip files that can't be parsed or accessed:
                        # - XMLSyntaxError: malformed XML
                        # - OSError: file access issues
                        # - PermissionError: insufficient permissions
                        continue


def parse_message_from_wsdl(
    root, message_name: str, namespaces: dict, schema_context: dict
) -> Dict[str, Any]:
    """
    Parse a WSDL message definition to extract parameter details.
    Returns a dictionary with message name and parameters.
    """
    # Find the message definition
    message = root.find(f".//wsdl:message[@name='{message_name}']", namespaces)

    if message is None:
        return {"name": message_name, "parameters": []}

    parameters = []

    # Get all parts in the message
    for part in message.findall("wsdl:part", namespaces):
        part_name = part.get("name")
        part_element = part.get("element")
        part_type = part.get("type")

        if part_element:
            # Element reference - need to resolve the element
            element_name = part_element.split(":")[-1]
            element_info = resolve_element_type(
                element_name, namespaces, schema_context
            )
            if element_info:
                parameters.extend(element_info)
        elif part_type:
            # Direct type reference
            type_name = part_type.split(":")[-1]
            parameters.append(
                {
                    "name": part_name,
                    "type": type_name,
                    "minOccurs": "1",
                    "maxOccurs": "1",
                    "is_attribute": False,
                    "documentation": None,
                    "children": [],
                }
            )

    return {"name": message_name, "parameters": parameters}


def resolve_element_type(
    element_name: str,
    namespaces: dict,
    schema_context: dict,
    depth: int = 0,
    visited: set = None,
) -> list:
    """
    Resolve an element definition from the schema to get its parameters recursively.

    Args:
        element_name: Name of the element to resolve
        namespaces: XML namespaces
        schema_context: Dictionary containing all loaded schema roots
        depth: Current recursion depth for nested types
        visited: Set of already visited type names to prevent infinite recursion

    Returns:
        List of parameter dictionaries with detailed information
    """
    if visited is None:
        visited = set()

    # Prevent infinite recursion
    if depth > 10 or element_name in visited:
        return []

    visited.add(element_name)
    parameters = []

    # Search for element in all loaded schemas
    element = None
    for root in schema_context["roots"]:
        element = root.find(f".//xs:element[@name='{element_name}']", namespaces)
        if element is not None:
            break

    if element is None:
        return parameters

    # Get element documentation
    doc_elem = element.find("xs:annotation/xs:documentation", namespaces)
    if doc_elem is not None:
        full_text = extract_documentation_text(doc_elem)
        if full_text:
            clean_documentation_html(full_text)

    # Check if it has a complexType
    complex_type = element.find("xs:complexType", namespaces)
    type_name = None

    if complex_type is None:
        # Try to get the type attribute
        type_attr = element.get("type")
        if type_attr:
            type_name = type_attr.split(":")[-1]
            # Try to find the complexType definition in all schemas
            for root in schema_context["roots"]:
                complex_type = root.find(
                    f".//xs:complexType[@name='{type_name}']", namespaces
                )
                if complex_type is not None:
                    break

    if complex_type is not None:
        # First, get attributes (xs:attribute) - these come FIRST in display
        for attr in complex_type.findall("xs:attribute", namespaces):
            attr_name = attr.get("name")
            attr_type = attr.get("type", "").split(":")[-1]
            attr_use = attr.get("use", "optional")  # default is optional

            # Get documentation for this attribute
            attr_doc = None
            attr_doc_elem = attr.find("xs:annotation/xs:documentation", namespaces)
            if attr_doc_elem is not None:
                full_text = extract_documentation_text(attr_doc_elem)
                if full_text:
                    attr_doc = clean_documentation_html(full_text)

            attr_info = {
                "name": attr_name,
                "type": attr_type,
                "minOccurs": "1" if attr_use == "required" else "0",
                "maxOccurs": "1",
                "documentation": attr_doc,
                "children": [],
                "is_attribute": True,  # Mark as attribute
            }

            parameters.append(attr_info)

        # Then, get sequence elements (xs:element)
        sequence = complex_type.find("xs:sequence", namespaces)
        if sequence is not None:
            for elem in sequence.findall("xs:element", namespaces):
                param_name = elem.get("name")
                param_type = elem.get("type", "").split(":")[-1]
                min_occurs = elem.get("minOccurs", "1")
                max_occurs = elem.get("maxOccurs", "1")

                # Get documentation for this element
                param_doc = None
                param_doc_elem = elem.find("xs:annotation/xs:documentation", namespaces)
                if param_doc_elem is not None:
                    full_text = extract_documentation_text(param_doc_elem)
                    if full_text:
                        param_doc = clean_documentation_html(full_text)

                param_info = {
                    "name": param_name,
                    "type": param_type,
                    "minOccurs": min_occurs,
                    "maxOccurs": max_occurs,
                    "documentation": param_doc,
                    "children": [],
                    "is_attribute": False,  # Mark as element
                }

                # Check if element has inline complexType (nested structure without type reference)
                inline_complex = elem.find("xs:complexType", namespaces)
                if inline_complex is not None:
                    # Parse inline complexType
                    inline_children = parse_inline_complex_type(
                        inline_complex,
                        namespaces,
                        schema_context,
                        depth + 1,
                        visited.copy(),
                    )
                    if inline_children:
                        param_info["children"] = inline_children
                # Recursively resolve complex types by reference
                elif (
                    param_type
                    and not param_type.startswith("xs:")
                    and param_type
                    not in [
                        "string",
                        "int",
                        "boolean",
                        "float",
                        "dateTime",
                        "anyURI",
                        "duration",
                        "base64Binary",
                    ]
                ):
                    # This might be a complex type, try to resolve it
                    child_params = resolve_complex_type(
                        param_type,
                        namespaces,
                        schema_context,
                        depth + 1,
                        visited.copy(),
                    )
                    if child_params:
                        param_info["children"] = child_params

                parameters.append(param_info)

    return parameters


def resolve_complex_type(
    type_name: str,
    namespaces: dict,
    schema_context: dict,
    depth: int = 0,
    visited: set = None,
) -> list:
    """
    Resolve a complexType definition to get its child elements.

    Args:
        type_name: Name of the complexType to resolve
        namespaces: XML namespaces
        schema_context: Dictionary containing all loaded schema roots
        depth: Current recursion depth
        visited: Set of visited types to prevent cycles

    Returns:
        List of child parameter dictionaries
    """
    if visited is None:
        visited = set()

    # Prevent infinite recursion
    if depth > 10 or type_name in visited:
        return []

    visited.add(type_name)
    children = []

    # Search for complexType definition in all schemas
    complex_type = None
    for root in schema_context["roots"]:
        complex_type = root.find(f".//xs:complexType[@name='{type_name}']", namespaces)
        if complex_type is not None:
            break

    if complex_type is None:
        return children

    # First, get attributes (xs:attribute)
    for attr in complex_type.findall("xs:attribute", namespaces):
        attr_name = attr.get("name")
        attr_type = attr.get("type", "").split(":")[-1]
        attr_use = attr.get("use", "optional")

        # Get documentation
        attr_doc = None
        attr_doc_elem = attr.find("xs:annotation/xs:documentation", namespaces)
        if attr_doc_elem is not None:
            full_text = extract_documentation_text(attr_doc_elem)
            if full_text:
                attr_doc = clean_documentation_html(full_text)

        attr_info = {
            "name": attr_name,
            "type": attr_type,
            "minOccurs": "1" if attr_use == "required" else "0",
            "maxOccurs": "1",
            "documentation": attr_doc,
            "children": [],
            "is_attribute": True,
        }

        children.append(attr_info)

    # Check for complexContent with extension or restriction
    complex_content = complex_type.find("xs:complexContent", namespaces)
    if complex_content is not None:
        # Handle extension
        extension = complex_content.find("xs:extension", namespaces)
        restriction = complex_content.find("xs:restriction", namespaces)

        content_element = extension if extension is not None else restriction

        if content_element is not None:
            # Get base type and recursively resolve it
            base_type = content_element.get("base")
            if base_type:
                base_type_name = base_type.split(":")[-1]
                # Recursively get children from base type
                base_children = resolve_complex_type(
                    base_type_name,
                    namespaces,
                    schema_context,
                    depth + 1,
                    visited.copy(),
                )
                if base_children:
                    children.extend(base_children)

            # Get attributes from extension/restriction
            for attr in content_element.findall("xs:attribute", namespaces):
                attr_name = attr.get("name")
                attr_type = attr.get("type", "").split(":")[-1]
                attr_use = attr.get("use", "optional")

                # Get documentation
                attr_doc = None
                attr_doc_elem = attr.find("xs:annotation/xs:documentation", namespaces)
                if attr_doc_elem is not None:
                    full_text = extract_documentation_text(attr_doc_elem)
                    if full_text:
                        attr_doc = clean_documentation_html(full_text)

                attr_info = {
                    "name": attr_name,
                    "type": attr_type,
                    "minOccurs": "1" if attr_use == "required" else "0",
                    "maxOccurs": "1",
                    "documentation": attr_doc,
                    "children": [],
                    "is_attribute": True,
                }

                children.append(attr_info)

            # Get sequence from extension/restriction
            sequence = content_element.find("xs:sequence", namespaces)
    else:
        # Direct sequence without complexContent
        sequence = complex_type.find("xs:sequence", namespaces)

    # Process sequence elements if found
    if sequence is not None:
        for elem in sequence.findall("xs:element", namespaces):
            child_name = elem.get("name")
            child_type = elem.get("type", "").split(":")[-1]
            min_occurs = elem.get("minOccurs", "1")
            max_occurs = elem.get("maxOccurs", "1")

            # Get documentation
            child_doc = None
            doc_elem = elem.find("xs:annotation/xs:documentation", namespaces)
            if doc_elem is not None:
                full_text = extract_documentation_text(doc_elem)
                if full_text:
                    child_doc = clean_documentation_html(full_text)

            child_info = {
                "name": child_name,
                "type": child_type,
                "minOccurs": min_occurs,
                "maxOccurs": max_occurs,
                "documentation": child_doc,
                "children": [],
                "is_attribute": False,
            }

            # Check if element has inline complexType
            inline_complex = elem.find("xs:complexType", namespaces)
            if inline_complex is not None:
                # Parse inline complexType
                inline_children = parse_inline_complex_type(
                    inline_complex,
                    namespaces,
                    schema_context,
                    depth + 1,
                    visited.copy(),
                )
                if inline_children:
                    child_info["children"] = inline_children
            # Recursively resolve nested complex types by reference
            elif (
                child_type
                and not child_type.startswith("xs:")
                and child_type
                not in [
                    "string",
                    "int",
                    "boolean",
                    "float",
                    "dateTime",
                    "anyURI",
                    "duration",
                    "base64Binary",
                ]
            ):
                nested_children = resolve_complex_type(
                    child_type, namespaces, schema_context, depth + 1, visited.copy()
                )
                if nested_children:
                    child_info["children"] = nested_children

            children.append(child_info)

    return children


def parse_inline_complex_type(
    complex_type,
    namespaces: dict,
    schema_context: dict,
    depth: int = 0,
    visited: set = None,
) -> list:
    """
    Parse an inline complexType element (not referenced by name).

    Args:
        complex_type: The xs:complexType element itself
        namespaces: XML namespaces
        schema_context: Dictionary containing all loaded schema roots
        depth: Current recursion depth
        visited: Set of visited types

    Returns:
        List of child parameter dictionaries
    """
    if visited is None:
        visited = set()

    # Prevent infinite recursion
    if depth > 10:
        return []

    children = []

    # First, get attributes (xs:attribute)
    for attr in complex_type.findall("xs:attribute", namespaces):
        attr_name = attr.get("name")
        attr_type = attr.get("type", "").split(":")[-1]
        attr_use = attr.get("use", "optional")

        # Get documentation
        attr_doc = None
        attr_doc_elem = attr.find("xs:annotation/xs:documentation", namespaces)
        if attr_doc_elem is not None:
            full_text = extract_documentation_text(attr_doc_elem)
            if full_text:
                attr_doc = clean_documentation_html(full_text)

        attr_info = {
            "name": attr_name,
            "type": attr_type,
            "minOccurs": "1" if attr_use == "required" else "0",
            "maxOccurs": "1",
            "documentation": attr_doc,
            "children": [],
            "is_attribute": True,
        }

        children.append(attr_info)

    # Check for complexContent with extension or restriction
    complex_content = complex_type.find("xs:complexContent", namespaces)
    if complex_content is not None:
        # Handle extension
        extension = complex_content.find("xs:extension", namespaces)
        restriction = complex_content.find("xs:restriction", namespaces)

        content_element = extension if extension is not None else restriction

        if content_element is not None:
            # Get base type and recursively resolve it
            base_type = content_element.get("base")
            if base_type:
                base_type_name = base_type.split(":")[-1]
                # Recursively get children from base type
                base_children = resolve_complex_type(
                    base_type_name,
                    namespaces,
                    schema_context,
                    depth + 1,
                    visited.copy(),
                )
                if base_children:
                    children.extend(base_children)

            # Get attributes from extension/restriction
            for attr in content_element.findall("xs:attribute", namespaces):
                attr_name = attr.get("name")
                attr_type = attr.get("type", "").split(":")[-1]
                attr_use = attr.get("use", "optional")

                # Get documentation
                attr_doc = None
                attr_doc_elem = attr.find("xs:annotation/xs:documentation", namespaces)
                if attr_doc_elem is not None:
                    full_text = extract_documentation_text(attr_doc_elem)
                    if full_text:
                        attr_doc = clean_documentation_html(full_text)

                attr_info = {
                    "name": attr_name,
                    "type": attr_type,
                    "minOccurs": "1" if attr_use == "required" else "0",
                    "maxOccurs": "1",
                    "documentation": attr_doc,
                    "children": [],
                    "is_attribute": True,
                }

                children.append(attr_info)

            # Get sequence from extension/restriction
            sequence = content_element.find("xs:sequence", namespaces)
    else:
        # Direct sequence without complexContent
        sequence = complex_type.find("xs:sequence", namespaces)

    # Process sequence elements if found
    if sequence is not None:
        for elem in sequence.findall("xs:element", namespaces):
            child_name = elem.get("name")
            child_type = elem.get("type", "").split(":")[-1]
            min_occurs = elem.get("minOccurs", "1")
            max_occurs = elem.get("maxOccurs", "1")

            # Get documentation
            child_doc = None
            doc_elem = elem.find("xs:annotation/xs:documentation", namespaces)
            if doc_elem is not None:
                full_text = extract_documentation_text(doc_elem)
                if full_text:
                    child_doc = clean_documentation_html(full_text)

            child_info = {
                "name": child_name,
                "type": child_type,
                "minOccurs": min_occurs,
                "maxOccurs": max_occurs,
                "documentation": child_doc,
                "children": [],
                "is_attribute": False,
            }

            # Check if element has nested inline complexType
            nested_inline = elem.find("xs:complexType", namespaces)
            if nested_inline is not None:
                # Recursively parse nested inline complexType
                nested_children = parse_inline_complex_type(
                    nested_inline, namespaces, schema_context, depth + 1, visited.copy()
                )
                if nested_children:
                    child_info["children"] = nested_children
            # Recursively resolve complex types by reference
            elif (
                child_type
                and not child_type.startswith("xs:")
                and child_type
                not in [
                    "string",
                    "int",
                    "boolean",
                    "float",
                    "dateTime",
                    "anyURI",
                    "duration",
                    "base64Binary",
                ]
            ):
                nested_children = resolve_complex_type(
                    child_type, namespaces, schema_context, depth + 1, visited.copy()
                )
                if nested_children:
                    child_info["children"] = nested_children

            children.append(child_info)

    return children
