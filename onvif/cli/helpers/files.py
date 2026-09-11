"""File processing helpers."""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any

from onvif.cli.utils import colorize
from onvif.client import ONVIFClient


def save_output_to_file(
    result: Any, output_path: str, debug_mode: bool, client: ONVIFClient
) -> None:
    """Save command output to file in appropriate format based on file extension.

    Args:
        result (Any): The ONVIF command result
        output_path (str): Path to output file
        debug_mode (bool): Whether debug mode is enabled (for XML capture)
        client (ONVIFClient): ONVIFClient instance (for accessing XML plugin)
    """
    try:
        # Determine output format based on file extension
        _, ext = os.path.splitext(output_path.lower())

        if ext == ".json":
            # Prepare output data
            output_data = {}

            # JSON format
            output_data["result"] = _serialize_for_json(result)
            output_data["timestamp"] = datetime.now(timezone.utc).isoformat()
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
<!-- Timestamp: {datetime.now(timezone.utc).isoformat()} -->
<!-- Operation: {client.xml_plugin.last_operation or 'Unknown'} -->

{client.xml_plugin.last_received_xml}
"""
            else:
                # Fallback: Simple XML wrapper for the parsed result
                content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- ONVIF Command Output (Parsed Result) -->
<!-- Timestamp: {datetime.now(timezone.utc).isoformat()} -->
<!-- Note: Raw SOAP XML not available. Enable --debug for full SOAP capture. -->
<onvif_result>
<![CDATA[
{result!s}
]]>
</onvif_result>
"""

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

        else:
            # Plain text format (default)
            content = "ONVIF Command Output\n"
            content += f"Timestamp: {datetime.now(timezone.utc).isoformat()}\n"
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

    except (AttributeError, ValueError, OSError) as e:
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
        if hasattr(obj._xsd_type, "elements"):  # pylint: disable=protected-access
            for (
                elem_name,
                _,
            ) in obj._xsd_type.elements:  # pylint: disable=protected-access
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
        return _serialize_for_json(obj._value_1)  # pylint: disable=protected-access
    else:
        # Try to convert to dict using vars() if available
        try:
            obj_dict = vars(obj)
            return _serialize_for_json(obj_dict)
        except TypeError:
            # Fallback to string representation
            return str(obj)
