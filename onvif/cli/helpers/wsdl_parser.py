"""ONVIF WSDL parser helpers."""

import inspect
import os
import re
from typing import Any, TypedDict

from lxml import etree

from onvif.cli.utils import colorize


class ParameterInfo(TypedDict):
    """Parameter information."""

    name: str | None
    type: str | None
    minOccurs: str
    maxOccurs: str
    is_attribute: bool
    documentation: str | None
    children: list["ParameterInfo"]


class MessageInfo(TypedDict):
    """Message information."""

    name: str
    parameters: list[ParameterInfo]


class OperationTypeInfo(TypedDict):
    """Operation information."""

    input: MessageInfo | None
    output: MessageInfo | None


def get_method_documentation(service_obj, method_name: str) -> dict[str, Any] | None:
    """Extracts documentation from WSDL and parameters from the Python method signature.

    Returns a dictionary with 'doc', 'required', and 'optional' keys.
    """
    doc_text = "No documentation available."
    required_args: list[str] = []
    optional_args: list[str] = []

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

    except (etree.ParseError, FileNotFoundError, AttributeError, ValueError, OSError):
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
    except RuntimeError:
        return None


def get_operation_type_info(
    service_obj, operation_name: str
) -> OperationTypeInfo | None:
    """Extract input and output message types from WSDL for a given operation.

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

        result: OperationTypeInfo = {"input": None, "output": None}

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

    except (OSError, etree.XMLSyntaxError):
        return None


def parse_message_from_wsdl(
    root, message_name: str, namespaces: dict, schema_context: dict
) -> MessageInfo | None:
    """Parse a WSDL message definition to extract parameter details.

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


def clean_documentation_html(doc_text: str) -> str:
    """Clean HTML tags from documentation text and convert links to readable format.

    Args:
        doc_text: Documentation text that may contain HTML tags

    Returns:
        Cleaned text with HTML tags removed and links converted
    """
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
    """Extract full text from xs:documentation element including child elements.

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


def _load_imported_schemas(root, schema_context: dict, namespaces: dict):
    """Recursively load all imported and included schemas into the schema context."""
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


def resolve_element_type(
    element_name: str,
    namespaces: dict,
    schema_context: dict,
    depth: int = 0,
    visited: set[str] | None = None,
) -> list:
    """Resolve an element definition from the schema to get its parameters recursively.

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
    parameters: list[dict[str, Any]] = []

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
    visited: set[str] | None = None,
) -> list:
    """Resolve a complexType definition to get its child elements.

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
    children: list[dict[str, Any]] = []
    sequence = None

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
    visited: set[str] | None = None,
) -> list:
    """Parse an inline complexType element (not referenced by name).

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
    sequence = None

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
