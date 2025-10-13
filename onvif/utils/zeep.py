# onvif/utils/zeep.py

from lxml.etree import QName
from zeep.xsd.elements.any import Any
from zeep.xsd.utils import max_occurs_iter


def parse_text_value(value):
    if value is None:
        return None
    val = value.strip()
    if val.lower() == "true":
        return True
    elif val.lower() == "false":
        return False
    elif val.isdigit():
        return int(val)
    try:
        return float(val)
    except ValueError:
        return val


def flatten_xsd_any_fields(obj, _visited=None):
    """
    Post-process zeep objects to flatten xsd:any fields (_value_1, _value_2, etc.) into the main object.

    Zeep uses _value_N fields to store parsed content from xsd:any elements. This function:
    1. Extracts the parsed data from _value_N (which is initially a dict)
    2. Copies values from _value_N to None fields in the main object
    3. Restores _value_N to contain the original XML elements (for zeep compatibility)

    This handles all xsd:any occurrences (_value_1, _value_2, _value_3, etc.), not just the first one.

    Args:
        obj: The zeep object to process
        _visited: Set of visited object IDs to prevent infinite recursion

    Returns:
        The processed object with flattened fields and restored _value_N
    """
    # Track visited objects to prevent infinite recursion
    if _visited is None:
        _visited = set()

    # Handle list of objects
    if isinstance(obj, list):
        for item in obj:
            flatten_xsd_any_fields(item, _visited)
        return obj

    obj_id = id(obj)
    if obj_id in _visited:
        return obj
    _visited.add(obj_id)

    # Skip primitive types
    if isinstance(obj, (dict, str, int, float, bool, type(None))):
        return obj

    if not hasattr(obj, "__dict__"):
        return obj

    # Check if object is a zeep object with __values__
    if hasattr(obj, "__values__"):
        values = obj.__values__

        # Process all _value_N fields (xsd:any can have maxOccurs > 1)
        value_n = 1
        while f"_value_{value_n}" in values:
            value_key = f"_value_{value_n}"
            value_data = values[value_key]

            # Only process if _value_N is a dict (from our patched parser)
            if isinstance(value_data, dict) and "__original_elements__" in value_data:
                # Extract original elements first
                original_elements = value_data.get("__original_elements__")

                # Check if this is a single-tag wrapper (like {"Capabilities": {...}})
                # IMPORTANT: We should NOT flatten if the tag name already exists as a field in the schema
                # This prevents DeviceIO, Recording, etc. from being incorrectly flattened
                non_private_keys = [k for k in value_data.keys() if not k.startswith("_")]
                
                if len(non_private_keys) == 1:
                    # Single tag wrapper - but check if it should be flattened
                    tag_name = non_private_keys[0]
                    inner_content = value_data[tag_name]
                    
                    # Only flatten if:
                    # 1. The tag_name field exists in schema AND is None (placeholder)
                    # 2. The inner_content is a dict (structured data)
                    # This preserves proper structure for DeviceIO, Recording, etc.
                    should_flatten = (
                        tag_name in values and 
                        values[tag_name] is None and 
                        isinstance(inner_content, dict)
                    )
                    
                    if should_flatten:
                        # This is truly a wrapper - flatten by copying fields to parent
                        # But still set the tag_name field to the inner_content
                        values[tag_name] = inner_content
                        # Don't copy fields up to parent - keep them in the structured object
                    else:
                        # Not a wrapper - just set the field directly
                        if tag_name in values and values[tag_name] is None:
                            values[tag_name] = inner_content
                        elif tag_name not in values:
                            values[tag_name] = inner_content
                else:
                    # Multiple tags - copy all non-private fields to their respective locations
                    for key, val in list(value_data.items()):
                        if key.startswith("_"):
                            continue
                        
                        if key in values and values[key] is None:
                            values[key] = val
                        elif key not in values:
                            values[key] = val

                # Replace _value_N with ONLY the original elements list
                if original_elements is not None:
                    values[value_key] = original_elements
                else:
                    values[value_key] = None

            value_n += 1

    # Also check if object has _value_N attributes in __dict__ (for non-zeep objects)
    else:
        value_n = 1
        while hasattr(obj, f"_value_{value_n}"):
            value_key = f"_value_{value_n}"
            value_data = getattr(obj, value_key)

            if isinstance(value_data, dict) and "__original_elements__" in value_data:
                # Extract original elements first (before any modification)
                original_elements = value_data.get("__original_elements__")

                # Check if this is a single-tag wrapper
                non_private_keys = [k for k in value_data.keys() if not k.startswith("_")]
                
                if len(non_private_keys) == 1:
                    # Single tag wrapper - but check if it should be flattened
                    tag_name = non_private_keys[0]
                    inner_content = value_data[tag_name]
                    
                    # Only flatten if the tag_name field exists and is None (placeholder)
                    should_flatten = (
                        hasattr(obj, tag_name) and 
                        getattr(obj, tag_name) is None and
                        isinstance(inner_content, dict)
                    )
                    
                    if should_flatten:
                        # Set the field to the structured content
                        setattr(obj, tag_name, inner_content)
                    else:
                        # Not a wrapper - just set the field directly
                        if hasattr(obj, tag_name) and getattr(obj, tag_name) is None:
                            setattr(obj, tag_name, inner_content)
                        elif not hasattr(obj, tag_name):
                            setattr(obj, tag_name, inner_content)
                else:
                    # Multiple tags - copy all non-private fields
                    for key, val in value_data.items():
                        if key.startswith("_"):
                            continue
                        
                        if hasattr(obj, key) and getattr(obj, key) is None:
                            setattr(obj, key, val)
                        elif not hasattr(obj, key):
                            setattr(obj, key, val)

                # Replace _value_N with ONLY the original elements list
                if original_elements is not None:
                    setattr(obj, value_key, original_elements)
                else:
                    setattr(obj, value_key, None)

            value_n += 1

    # Recursively process nested objects
    if hasattr(obj, "__values__"):
        for val in obj.__values__.values():
            if val is not None and not isinstance(val, (dict, str, int, float, bool)):
                if hasattr(val, "__dict__"):
                    flatten_xsd_any_fields(val, _visited)
                elif isinstance(val, list):
                    for item in val:
                        if hasattr(item, "__dict__"):
                            flatten_xsd_any_fields(item, _visited)
    else:
        for key, val in list(obj.__dict__.items()):
            if val is not None and not isinstance(val, (dict, str, int, float, bool)):
                if hasattr(val, "__dict__"):
                    flatten_xsd_any_fields(val, _visited)
                elif isinstance(val, list):
                    for item in val:
                        if hasattr(item, "__dict__"):
                            flatten_xsd_any_fields(item, _visited)

    return obj


def patched_parse_xmlelements(self, xmlelements, schema, name=None, context=None):
    parsed_result = {}
    original_elements = []  # Store original XML elements

    for _ in max_occurs_iter(self.max_occurs):
        if not xmlelements:
            break
        xmlelement = xmlelements.popleft()

        # Store original element before processing
        original_elements.append(xmlelement)

        tag_name = QName(xmlelement.tag).localname
        children = list(xmlelement)
        if children and schema:
            child_result = {}
            for child in children:
                child_qname = QName(child.tag)
                try:
                    xsd_el = schema.get_element(child_qname)
                    val = xsd_el.parse_xmlelement(
                        child, schema=schema, allow_none=True, context=context
                    )
                    child_result[child_qname.localname] = val
                except Exception:
                    # If schema lookup fails, try to parse manually
                    # Check if child has attributes (common in ONVIF capabilities)
                    if child.attrib:
                        # Parse attributes as a dict
                        attr_dict = {k: parse_text_value(v) for k, v in child.attrib.items()}
                        child_result[child_qname.localname] = attr_dict
                    elif list(child):
                        # Has nested children
                        nested = {
                            QName(sub.tag).localname: parse_text_value(sub.text)
                            for sub in child
                        }
                        child_result[child_qname.localname] = nested
                    else:
                        # Only has text content
                        child_result[child_qname.localname] = parse_text_value(
                            child.text
                        )
            parsed_result[tag_name] = child_result
        else:
            parsed_result[tag_name] = parse_text_value(xmlelement.text)

    # Store original elements in a special key for later restoration
    if original_elements:
        parsed_result["__original_elements__"] = original_elements

    return parsed_result


# Store original parse_xmlelements before patching
_original_parse_xmlelements = None
_is_patched = False


def apply_patch():
    """Inject the custom parse_xmlelements method into zeep.xsd.elements.any.Any."""
    global _original_parse_xmlelements, _is_patched

    if not _is_patched:
        _original_parse_xmlelements = Any.parse_xmlelements
        Any.parse_xmlelements = patched_parse_xmlelements
        _is_patched = True


def remove_patch():
    """Restore the original parse_xmlelements method."""
    global _is_patched

    if _is_patched and _original_parse_xmlelements is not None:
        Any.parse_xmlelements = _original_parse_xmlelements
        _is_patched = False


def is_patched():
    """Check if the patch is currently applied."""
    return _is_patched
