"""Generate JSON metadata from local ONVIF WSDL and XSD files."""

from __future__ import annotations

import html
import json
from html import escape
from pathlib import Path
from typing import Any

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
WSDL_DIR = ROOT / "onvif" / "wsdl"
OUTPUT_DIR = ROOT / "docs" / "generated" / "wsdl"

WSDL_NS = "http://schemas.xmlsoap.org/wsdl/"
XSD_NS = "http://www.w3.org/2001/XMLSchema"
SOAP_NS = "http://schemas.xmlsoap.org/wsdl/soap/"

NS = {"wsdl": WSDL_NS, "xsd": XSD_NS, "soap": SOAP_NS}

PARSER = etree.XMLParser(
    resolve_entities=False,
    no_network=True,
    load_dtd=False,
    huge_tree=False,
    remove_comments=True,
)


def qname(value: str | None, node: etree._Element) -> str | None:
    """Resolve a lexical QName to Clark notation."""
    if not value:
        return None

    try:
        return _resolve_qname(value, node)
    except (ValueError, KeyError):
        return value


def _resolve_qname(value: str, node: etree._Element) -> str:
    """Resolve a QName using the namespace declarations in scope."""
    if value.startswith("{"):
        return value

    if ":" in value:
        prefix, local = value.split(":", 1)
        namespace = node.nsmap.get(prefix)
        if namespace is None:
            raise ValueError(f"Undeclared QName prefix: {prefix}")
        return f"{{{namespace}}}{local}"

    # An unprefixed QName uses the default namespace when declared.
    namespace = node.nsmap.get(None)
    return f"{{{namespace}}}{value}" if namespace else value


def local_name(value: str | None) -> str | None:
    """Return the local part of a QName."""
    if not value:
        return None
    return etree.QName(value).localname if value.startswith("{") else value


def parse_xml(path: Path) -> etree._ElementTree:
    """Parse an XML document without network access or entity expansion."""
    return etree.parse(str(path), PARSER)


class WSDLMetadataGenerator:
    """Collect WSDL operations and resolve their XML schema structures."""

    def __init__(self, wsdl_dir: Path) -> None:
        self.wsdl_dir = wsdl_dir
        self.documents: dict[Path, etree._ElementTree] = {}
        self.elements: dict[str, etree._Element] = {}
        self.types: dict[str, etree._Element] = {}
        self.messages: dict[str, etree._Element] = {}
        self.port_types: dict[str, etree._Element] = {}
        self.bindings: dict[str, etree._Element] = {}
        self._load_documents()

    def _load_documents(self) -> None:
        """Load WSDL/XSD documents and index global declarations."""
        paths = sorted(
            path
            for path in self.wsdl_dir.rglob("*")
            if path.suffix.lower() in {".wsdl", ".xsd"}
        )

        for path in paths:
            tree = parse_xml(path)
            self.documents[path] = tree
            root = tree.getroot()
            target_ns = root.get("targetNamespace", "")

            if etree.QName(root).localname == "schema":
                self._index_schema(root, target_ns)
                continue

            for message in root.findall("wsdl:message", NS):
                name = message.get("name")
                if name:
                    self.messages[f"{{{target_ns}}}{name}"] = message

            for port_type in root.findall("wsdl:portType", NS):
                name = port_type.get("name")
                if name:
                    self.port_types[f"{{{target_ns}}}{name}"] = port_type

            for binding in root.findall("wsdl:binding", NS):
                name = binding.get("name")
                if name:
                    self.bindings[f"{{{target_ns}}}{name}"] = binding

            # Inline schemas inside wsdl:types.
            for schema in root.findall("wsdl:types/xsd:schema", NS):
                self._index_schema(schema, schema.get("targetNamespace", target_ns))

    def _index_schema(self, schema: etree._Element, target_ns: str) -> None:
        """Index global XSD elements and type declarations."""
        for element in schema.findall("xsd:element", NS):
            name = element.get("name")
            if name:
                self.elements[f"{{{target_ns}}}{name}"] = element

        for kind in ("complexType", "simpleType"):
            for node in schema.findall(f"xsd:{kind}", NS):
                name = node.get("name")
                if name:
                    self.types[f"{{{target_ns}}}{name}"] = node

    @staticmethod
    def _documentation(node: etree._Element) -> str | None:
        """Extract documentation and preserve safe embedded HTML markup."""
        annotation = node.find("xsd:annotation/xsd:documentation", NS)
        if annotation is None:
            return None

        allowed_tags = {
            "a",
            "b",
            "strong",
            "i",
            "em",
            "code",
            "p",
            "br",
            "ul",
            "ol",
            "li",
            "sub",
            "sup",
        }
        allowed_attributes = {"href", "title"}
        void_tags = {"br"}

        def render(element: etree._Element) -> str:
            """Render an XML documentation node as namespace-free HTML."""
            parts: list[str] = []
            tag = etree.QName(element).localname

            if tag in allowed_tags:
                attrs: list[str] = []

                for key, value in element.attrib.items():
                    attr_name = etree.QName(key).localname

                    if attr_name not in allowed_attributes:
                        continue

                    if attr_name == "href" and not value.strip().lower().startswith(
                        ("https://", "http://", "mailto:", "#", "/")
                    ):
                        continue

                    attrs.append(f' {attr_name}="{escape(value, quote=True)}"')

                parts.append(f"<{tag}{''.join(attrs)}>")

            parts.append(escape(html.unescape(element.text or ""), quote=False))

            for child in element:
                parts.append(render(child))
                parts.append(escape(html.unescape(child.tail or ""), quote=False))

            if tag in allowed_tags and tag not in void_tags:
                parts.append(f"</{tag}>")

            return "".join(parts)

        description = render(annotation).strip()
        return description or None

    # pylint: disable=too-many-branches
    def _schema_node(
        self,
        node: etree._Element,
        seen: frozenset[str] = frozenset(),
    ) -> dict[str, Any]:
        """Convert an XSD element or type into recursive JSON metadata."""
        kind = etree.QName(node).localname
        result: dict[str, Any] = {}

        name = node.get("name")
        ref = qname(node.get("ref"), node)
        type_name = qname(node.get("type"), node)

        if name:
            result["name"] = name

        if ref:
            result["ref"] = ref
            result.setdefault("name", local_name(ref))

            if ref in seen:
                result["recursive"] = True
            else:
                target = self.elements.get(ref)
                if target is not None:
                    resolved = self._schema_node(target, seen | {ref})
                    # Preserve the local element's occurrence constraints.
                    result = {**resolved, **result}
                else:
                    result["unresolved"] = True

        if type_name:
            result["type"] = type_name
            result["type_name"] = local_name(type_name)

            target_type = self.types.get(type_name)
            if target_type is not None:
                if type_name in seen:
                    result["recursive"] = True
                else:
                    result["definition"] = self._schema_definition(
                        target_type,
                        seen | {type_name},
                    )

        # Handle anonymous inline types.
        simple_type = node.find("xsd:simpleType", NS)
        complex_type = node.find("xsd:complexType", NS)

        if simple_type is not None:
            result["definition"] = self._schema_definition(simple_type, seen)
        elif complex_type is not None:
            result["definition"] = self._schema_definition(complex_type, seen)

        min_occurs = node.get("minOccurs")
        max_occurs = node.get("maxOccurs")

        if kind == "element":
            result["min_occurs"] = int(min_occurs or "1")
            result["max_occurs"] = (
                "unbounded" if max_occurs == "unbounded" else int(max_occurs or "1")
            )
            result["nillable"] = node.get("nillable", "false") == "true"

        description = self._documentation(node)
        if description:
            result["description"] = description

        for attribute in ("default", "fixed"):
            value = node.get(attribute)
            if value is not None:
                result[attribute] = value

        return result

    def _schema_children(
        self,
        node: etree._Element,
        seen: frozenset[str],
    ) -> list[dict[str, Any]]:
        """Collect immediate elements from XSD compositors."""
        children: list[dict[str, Any]] = []

        compositor_tags = {
            f"{{{XSD_NS}}}sequence",
            f"{{{XSD_NS}}}choice",
            f"{{{XSD_NS}}}all",
        }

        def visit(parent: etree._Element) -> None:
            for child in parent:
                if child.tag == f"{{{XSD_NS}}}element":
                    children.append(self._schema_node(child, seen))
                elif child.tag in compositor_tags:
                    visit(child)
                elif child.tag == f"{{{XSD_NS}}}group":
                    # Group references require a global group index.
                    group_ref = qname(child.get("ref"), child)
                    if group_ref:
                        children.append(
                            {
                                "kind": "group",
                                "ref": group_ref,
                                "min_occurs": int(child.get("minOccurs", "1")),
                                "max_occurs": (
                                    "unbounded"
                                    if child.get("maxOccurs") == "unbounded"
                                    else int(child.get("maxOccurs", "1"))
                                ),
                            }
                        )

        visit(node)
        return children

    # pylint: disable=too-many-branches
    def _schema_definition(
        self,
        node: etree._Element,
        seen: frozenset[str],
    ) -> dict[str, Any]:
        """Resolve simpleType and complexType definitions."""
        kind = etree.QName(node).localname
        result: dict[str, Any] = {"kind": kind}

        if node.get("name"):
            result["name"] = node.get("name")

        description = self._documentation(node)
        if description:
            result["description"] = description

        if kind == "simpleType":
            restriction = node.find(
                "xsd:restriction",
                NS,
            )

            if restriction is not None:
                base = qname(restriction.get("base"), restriction)
                if base:
                    result["base"] = base

                    base_type = self.types.get(base)
                    if base_type is not None and base not in seen:
                        result["base_definition"] = self._schema_definition(
                            base_type,
                            seen | {base},
                        )

                enumerations = []
                for item in restriction.findall("xsd:enumeration", NS):
                    entry: dict[str, Any] = {"value": item.get("value")}
                    item_description = self._documentation(item)
                    if item_description:
                        entry["description"] = item_description
                    enumerations.append(entry)

                if enumerations:
                    result["enumeration"] = enumerations

                for facet in (
                    "minInclusive",
                    "maxInclusive",
                    "minExclusive",
                    "maxExclusive",
                    "minLength",
                    "maxLength",
                    "length",
                    "pattern",
                    "totalDigits",
                    "fractionDigits",
                    "whiteSpace",
                ):
                    values = [
                        item.get("value")
                        for item in restriction.findall(
                            f"xsd:{facet}",
                            NS,
                        )
                    ]
                    if values:
                        result[facet] = values[0] if len(values) == 1 else values

            list_node = node.find("xsd:list", NS)
            if list_node is not None:
                item_type = qname(list_node.get("itemType"), list_node)
                if item_type:
                    result["item_type"] = item_type

                inline_item_type = list_node.find("xsd:simpleType", NS)
                if inline_item_type is not None:
                    result["item_definition"] = self._schema_definition(
                        inline_item_type,
                        seen,
                    )

            union_node = node.find("xsd:union", NS)
            if union_node is not None:
                result["member_types"] = [
                    qname(value, union_node)
                    for value in union_node.get("memberTypes", "").split()
                ]

        elif kind == "complexType":
            complex_content = node.find("xsd:complexContent", NS)
            simple_content = node.find("xsd:simpleContent", NS)
            content = complex_content if complex_content is not None else simple_content

            extension = None
            if content is not None:
                extension = content.find("xsd:extension", NS)
                if extension is None:
                    extension = content.find("xsd:restriction", NS)

            if extension is not None:
                base = qname(extension.get("base"), extension)
                if base:
                    result["base"] = base
                    base_type = self.types.get(base)

                    if base_type is not None:
                        if base in seen:
                            result["base_recursive"] = True
                        else:
                            result["base_definition"] = self._schema_definition(
                                base_type,
                                seen | {base},
                            )

                result["fields"] = self._schema_children(extension, seen)

                attributes_parent = extension
            else:
                result["fields"] = self._schema_children(node, seen)
                attributes_parent = node

            attributes: list[dict[str, Any]] = []
            for attr in attributes_parent.findall(".//xsd:attribute", NS):
                item: dict[str, Any] = {
                    "use": attr.get("use", "optional"),
                }

                if attr.get("name"):
                    item["name"] = attr.get("name")

                attr_ref = qname(attr.get("ref"), attr)
                attr_type = qname(attr.get("type"), attr)

                if attr_ref:
                    item["ref"] = attr_ref
                if attr_type:
                    item["type"] = attr_type
                    target_type = self.types.get(attr_type)
                    if target_type is not None and attr_type not in seen:
                        item["definition"] = self._schema_definition(
                            target_type,
                            seen | {attr_type},
                        )

                for key in ("default", "fixed"):
                    value = attr.get(key)
                    if value is not None:
                        item[key] = value

                attr_description = self._documentation(attr)
                if attr_description:
                    item["description"] = attr_description

                attributes.append(item)

            if attributes:
                result["attributes"] = attributes

            any_element = attributes_parent.find(".//xsd:any", NS)
            if any_element is not None:
                result["any"] = {
                    "namespace": any_element.get("namespace", "##any"),
                    "process_contents": any_element.get(
                        "processContents",
                        "strict",
                    ),
                    "min_occurs": int(any_element.get("minOccurs", "1")),
                    "max_occurs": (
                        "unbounded"
                        if any_element.get("maxOccurs") == "unbounded"
                        else int(any_element.get("maxOccurs", "1"))
                    ),
                }

            any_attribute = attributes_parent.find(
                ".//xsd:anyAttribute",
                NS,
            )
            if any_attribute is not None:
                result["any_attribute"] = {
                    "namespace": any_attribute.get("namespace", "##any"),
                    "process_contents": any_attribute.get(
                        "processContents",
                        "strict",
                    ),
                }

        return result

    def _message_parts(self, message_ref: str | None) -> list[dict[str, Any]]:
        """Resolve a WSDL message into its parameter parts."""
        if not message_ref:
            return []

        message = self.messages.get(message_ref)
        if message is None:
            return [{"message": message_ref, "unresolved": True}]

        parts: list[dict[str, Any]] = []

        for part in message.findall("wsdl:part", NS):
            name = part.get("name")
            element_ref = qname(part.get("element"), part)
            type_ref = qname(part.get("type"), part)

            item: dict[str, Any] = {"name": name}

            if element_ref:
                item["element"] = element_ref
                target = self.elements.get(element_ref)
                if target is not None:
                    item["schema"] = self._schema_node(target, frozenset({element_ref}))
                else:
                    item["unresolved"] = True

            if type_ref:
                item["type"] = type_ref
                target_type = self.types.get(type_ref)
                if target_type is not None:
                    item["schema"] = self._schema_node(
                        target_type, frozenset({type_ref})
                    )

            parts.append(item)

        return parts

    def _operations(self, wsdl_path: Path) -> list[dict[str, Any]]:
        """Extract operations and resolve their WSDL bindings."""
        tree = self.documents[wsdl_path]
        root = tree.getroot()
        target_ns = root.get("targetNamespace", "")
        operations: list[dict[str, Any]] = []

        for port_type in root.findall("wsdl:portType", NS):
            port_type_name = port_type.get("name")

            if not port_type_name:
                continue

            port_type_ref = (
                f"{{{target_ns}}}{port_type_name}" if target_ns else port_type_name
            )

            # Resolve bindings by their QName reference to this portType.
            bindings = [
                binding.get("name")
                for binding in self.bindings.values()
                if qname(binding.get("type"), binding) == port_type_ref
                and binding.get("name")
            ]

            for operation in port_type.findall("wsdl:operation", NS):
                name = operation.get("name")

                if not name:
                    continue

                input_node = operation.find("wsdl:input", NS)
                output_node = operation.find("wsdl:output", NS)
                fault_nodes = operation.findall("wsdl:fault", NS)

                input_ref = (
                    qname(input_node.get("message"), input_node)
                    if input_node is not None
                    else None
                )
                output_ref = (
                    qname(output_node.get("message"), output_node)
                    if output_node is not None
                    else None
                )

                doc = operation.find("wsdl:documentation", NS)
                description = (
                    " ".join("".join(doc.itertext()).split())
                    if doc is not None
                    else None
                )

                operation_metadata: dict[str, Any] = {
                    "name": name,
                    "port_type": port_type_name,
                    "description": description,
                    "input": {
                        "message": input_ref,
                        "parts": self._message_parts(input_ref),
                    },
                    "output": {
                        "message": output_ref,
                        "parts": self._message_parts(output_ref),
                    },
                    "faults": [
                        {
                            "name": fault.get("name"),
                            "message": qname(fault.get("message"), fault),
                        }
                        for fault in fault_nodes
                    ],
                }

                if len(bindings) == 1:
                    operation_metadata["binding"] = bindings[0]
                elif len(bindings) > 1:
                    operation_metadata["bindings"] = bindings

                operations.append(operation_metadata)

        return operations

    def generate(self) -> int:
        """Write one JSON file for each WSDL document."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        count = 0

        for path in sorted(self.documents):
            if path.suffix.lower() != ".wsdl":
                continue

            root = self.documents[path].getroot()
            target_ns = root.get("targetNamespace", "")
            relative = path.relative_to(self.wsdl_dir)

            # Preserve subdirectory names to avoid filename collisions.
            output_path = OUTPUT_DIR / relative.with_suffix(".json")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            metadata = {
                "source": relative.as_posix(),
                "target_namespace": target_ns,
                "operations": self._operations(path),
            }

            output_path.write_text(
                json.dumps(
                    metadata,
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            count += len(metadata["operations"])
            print(f"Generated {output_path.relative_to(ROOT)}")

        print(f"Generated metadata for {count} WSDL operations.")
        return count


def main() -> None:
    """Generate WSDL metadata to JSON."""
    if not WSDL_DIR.is_dir():
        raise SystemExit(f"WSDL directory not found: {WSDL_DIR}")

    generator = WSDLMetadataGenerator(WSDL_DIR)
    generator.generate()


if __name__ == "__main__":
    main()
