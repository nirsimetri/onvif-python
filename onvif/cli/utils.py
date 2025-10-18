# onvif/cli/utils.py

import json
import os
import inspect
from typing import Any, Dict, Optional
import xml.etree.ElementTree as ET
import re


# ONVIF namespace to service name mapping (used globally)
ONVIF_NAMESPACE_MAP = {
    "http://www.onvif.org/ver10/device/wsdl": "devicemgmt",
    "http://www.onvif.org/ver10/events/wsdl": "events",
    "http://www.onvif.org/ver20/imaging/wsdl": "imaging",
    "http://www.onvif.org/ver10/media/wsdl": "media",
    "http://www.onvif.org/ver20/media/wsdl": "media2",
    "http://www.onvif.org/ver20/ptz/wsdl": "ptz",
    "http://www.onvif.org/ver10/deviceIO/wsdl": "deviceio",
    "http://www.onvif.org/ver10/display/wsdl": "display",
    "http://www.onvif.org/ver20/analytics/wsdl": "analytics",
    "http://www.onvif.org/ver10/analyticsdevice/wsdl": "analyticsdevice",
    "http://www.onvif.org/ver10/accesscontrol/wsdl": "accesscontrol",
    "http://www.onvif.org/ver10/doorcontrol/wsdl": "doorcontrol",
    "http://www.onvif.org/ver10/accessrules/wsdl": "accessrules",
    "http://www.onvif.org/ver10/actionengine/wsdl": "actionengine",
    "http://www.onvif.org/ver10/provisioning/wsdl": "provisioning",
    "http://www.onvif.org/ver10/receiver/wsdl": "receiver",
    "http://www.onvif.org/ver10/recording/wsdl": "recording",
    "http://www.onvif.org/ver10/replay/wsdl": "replay",
    "http://www.onvif.org/ver10/schedule/wsdl": "schedule",
    "http://www.onvif.org/ver10/search/wsdl": "search",
    "http://www.onvif.org/ver10/thermal/wsdl": "thermal",
    "http://www.onvif.org/ver10/uplink/wsdl": "uplink",
    "http://www.onvif.org/ver10/advancedsecurity/wsdl": "security",
}


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
    try:
        return json.loads(params_str)
    except Exception:
        pass

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


def get_service_methods(service_obj) -> list:
    """Get list of available methods for a service"""
    methods = []
    for attr_name in dir(service_obj):
        if not attr_name.startswith("_") and callable(getattr(service_obj, attr_name)):
            # Skip operator attribute
            if attr_name != "operator":
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
        tree = ET.parse(wsdl_path)
        root = tree.getroot()
        namespaces = {
            node[0]: node[1] for node in ET.iterparse(wsdl_path, events=["start-ns"])
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
        method = getattr(service_obj, method_name)
        sig = inspect.signature(method)
        for param in sig.parameters.values():
            if param.name != "self":
                if param.default is inspect.Parameter.empty:
                    required_args.append(param.name)
                else:
                    optional_args.append(param.name)

        return {"doc": doc_text, "required": required_args, "optional": optional_args}

    except (ET.ParseError, FileNotFoundError, AttributeError, ValueError):
        # Fallback in case of any error, still try to get params
        try:
            method = getattr(service_obj, method_name)
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

    return None


def truncate_output(text: str, max_length: int = 1000) -> str:
    """Truncate output if too long"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + f"\n... (truncated, {len(text)} total chars)"


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
            except Exception:
                pass  # Fallback to no colors if error

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
        "Events": "events",
        "Imaging": "imaging",
        "Media": "media",
        "PTZ": "ptz",
        "Analytics": "analytics",
        "Extension": None,  # Handle extensions separately
    }

    for cap_name, service_func in service_map.items():
        if service_func and hasattr(capabilities, cap_name):
            cap = getattr(capabilities, cap_name)
            if cap and "XAddr" in cap:
                services.append(f"  {colorize(service_func, 'yellow')}")
                services.append(f"    XAddr: {cap['XAddr']}")

    # Handle extensions
    if hasattr(capabilities, "Extension") and capabilities.Extension:
        ext = capabilities.Extension
        ext_services = {
            "DeviceIO": "deviceio",
            "Recording": "recording",
            "Replay": "replay",
            "Search": "search",
            "AccessControl": "accesscontrol",
            "DoorControl": "doorcontrol",
            "AccessRules": "accessrules",
            "ActionEngine": "actionengine",
            "appmgmt": "appmgmt",
            "AuthenticationBehavior": "authenticationbehavior",
            "Credential": "credential",
            "Provisioning": "provisioning",
            "Receiver": "receiver",
            "Schedule": "schedule",
            "Thermal": "thermal",
            "Uplink": "uplink",
            "AdvancedSecurity": "security",
        }

        for ext_name, service_func in ext_services.items():
            if hasattr(ext, ext_name):
                ext_service = getattr(ext, ext_name)
                if ext_service and "XAddr" in ext_service:
                    services.append(f"  {colorize(service_func, 'yellow')}")
                    services.append(f"    XAddr: {ext_service['XAddr']}")

        # Handle nested extensions
        if hasattr(ext, "Extension") and ext.Extension:
            ext_ext = ext.Extension
            for ext_name, service_func in ext_services.items():
                if hasattr(ext_ext, ext_name):
                    ext_service = getattr(ext_ext, ext_name)
                    if ext_service and "XAddr" in ext_service:
                        services.append(f"  {colorize(service_func, 'yellow')}")
                        services.append(f"    XAddr: {ext_service['XAddr']}")

    if services:
        header = f"{colorize('Available Capabilities:', 'green')}"
        service_lines = "\n".join(services)
        result = f"{header}\n{service_lines}"
        return result
    else:
        return f"{colorize('No services found in capabilities', 'yellow')}"


def format_services_list(services_list) -> str:
    """Format GetServices response as service list with XAddr"""
    if not services_list:
        return f"{colorize('No services available', 'yellow')}"

    services = []
    header = f"{colorize('Available Services:', 'green')}"

    for service in services_list:
        namespace = getattr(service, "Namespace", "")
        xaddr = getattr(service, "XAddr", "")
        version = getattr(service, "Version", {})

        service_func = ONVIF_NAMESPACE_MAP.get(namespace, f"unknown({namespace})")

        services.append(f"  {colorize(service_func, 'cyan')}")
        services.append(f"    XAddr: {xaddr}")

        if version:
            major = getattr(version, "Major", "")
            minor = getattr(version, "Minor", "")
            if major and minor:
                services.append(f"    Version: {major}.{minor}")
            elif major:
                services.append(f"    Version: {major}")

    header = f"{colorize('Available Services:', 'green')}"
    service_lines = "\n".join(services)
    result = f"{header}\n{service_lines}"
    return result


def get_device_available_services(client) -> list:
    """Get list of services actually available on the connected device"""
    available_services = ["devicemgmt"]  # devicemgmt is always available

    # Check if device has services information
    if hasattr(client, "services") and client.services:
        for service in client.services:
            namespace = getattr(service, "Namespace", None)
            if namespace and namespace in ONVIF_NAMESPACE_MAP:
                service_name = ONVIF_NAMESPACE_MAP[namespace]
                if service_name not in available_services:
                    available_services.append(service_name)

    # Check capabilities as fallback
    elif hasattr(client, "capabilities") and client.capabilities:
        caps = client.capabilities

        # Check various capability attributes for service availability
        if hasattr(caps, "Events") and caps.Events:
            available_services.append("events")
        if hasattr(caps, "Imaging") and caps.Imaging:
            available_services.append("imaging")
        if hasattr(caps, "Media") and caps.Media:
            available_services.append("media")
        if hasattr(caps, "PTZ") and caps.PTZ:
            available_services.append("ptz")
        if hasattr(caps, "DeviceIO") and caps.DeviceIO:
            available_services.append("deviceio")
        if hasattr(caps, "Display") and caps.Display:
            available_services.append("display")
        if hasattr(caps, "Analytics") and caps.Analytics:
            available_services.append("analytics")

    return sorted(list(set(available_services)))  # Remove duplicates and sort
