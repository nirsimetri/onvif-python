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
    
    obj_id = id(obj)
    if obj_id in _visited:
        return obj
    _visited.add(obj_id)
    
    # Skip dict-like objects
    if isinstance(obj, (dict, list, str, int, float, bool, type(None))):
        return obj
    
    if not hasattr(obj, '__dict__'):
        return obj
    
    # Check if object is a zeep object with __values__
    if hasattr(obj, '__values__'):
        values = obj.__values__
        
        # Process all _value_N fields (xsd:any can have maxOccurs > 1)
        value_n = 1
        while f'_value_{value_n}' in values:
            value_key = f'_value_{value_n}'
            value_data = values[value_key]
            
            if value_data is not None:
                # Check if we have original elements stored
                original_elements = None
                if isinstance(value_data, dict) and '__original_elements__' in value_data:
                    original_elements = value_data.pop('__original_elements__')
                
                # Handle both dict and zeep object cases
                if isinstance(value_data, dict):
                    value_dict = value_data
                elif hasattr(value_data, '__dict__'):
                    value_dict = value_data.__dict__
                else:
                    value_dict = {}
                
                # Iterate through all keys in __values__
                for key in list(values.keys()):
                    # Skip private fields and _value_N fields themselves
                    if key.startswith('_'):
                        continue
                    
                    # If field is None and exists in _value_N, copy it
                    if values[key] is None and key in value_dict:
                        values[key] = value_dict[key]
                
                # Restore original XML elements to _value_N
                if original_elements is not None:
                    values[value_key] = original_elements
            
            value_n += 1
    
    # Also check if object has _value_N attributes in __dict__ (for non-zeep objects)
    else:
        value_n = 1
        while hasattr(obj, f'_value_{value_n}'):
            value_key = f'_value_{value_n}'
            value_data = getattr(obj, value_key)
            
            if value_data is not None:
                # Check if we have original elements stored
                original_elements = None
                if isinstance(value_data, dict) and '__original_elements__' in value_data:
                    original_elements = value_data.pop('__original_elements__')
                
                # Handle both dict and zeep object cases
                if isinstance(value_data, dict):
                    value_dict = value_data
                elif hasattr(value_data, '__dict__'):
                    value_dict = value_data.__dict__
                else:
                    value_dict = {}
                
                # Iterate through all attributes of the main object
                for key in list(obj.__dict__.keys()):
                    # Skip private fields and _value_N fields themselves
                    if key.startswith('_'):
                        continue
                    
                    val = getattr(obj, key)
                    
                    # If field is None and exists in _value_N, copy it
                    if val is None and key in value_dict:
                        setattr(obj, key, value_dict[key])
                
                # Restore original XML elements to _value_N
                if original_elements is not None:
                    setattr(obj, value_key, original_elements)
            
            value_n += 1
    
    # Recursively process nested objects
    if hasattr(obj, '__values__'):
        for val in obj.__values__.values():
            if val is not None and not isinstance(val, (dict, str, int, float, bool)):
                if hasattr(val, '__dict__'):
                    flatten_xsd_any_fields(val, _visited)
                elif isinstance(val, list):
                    for item in val:
                        if hasattr(item, '__dict__'):
                            flatten_xsd_any_fields(item, _visited)
    else:
        for key, val in list(obj.__dict__.items()):
            if val is not None and not isinstance(val, (dict, str, int, float, bool)):
                if hasattr(val, '__dict__'):
                    flatten_xsd_any_fields(val, _visited)
                elif isinstance(val, list):
                    for item in val:
                        if hasattr(item, '__dict__'):
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
                    if list(child):
                        nested = {
                            QName(sub.tag).localname: parse_text_value(sub.text)
                            for sub in child
                        }
                        child_result[child_qname.localname] = nested
                    else:
                        child_result[child_qname.localname] = parse_text_value(child.text)
            parsed_result[tag_name] = child_result
        else:
            parsed_result[tag_name] = parse_text_value(xmlelement.text)
    
    # Store original elements in a special key for later restoration
    if original_elements:
        parsed_result['__original_elements__'] = original_elements
    
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