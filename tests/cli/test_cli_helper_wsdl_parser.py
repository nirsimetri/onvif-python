"""Tests for ONVIF CLI WSDL parser helpers."""

from types import SimpleNamespace

from lxml import etree

from onvif.cli.helpers.wsdl_parser import (
    _load_imported_schemas,
    clean_documentation_html,
    extract_documentation_text,
    get_method_documentation,
    get_operation_type_info,
    parse_inline_complex_type,
    parse_message_from_wsdl,
    resolve_complex_type,
    resolve_element_type,
)

XS_NS = "http://www.w3.org/2001/XMLSchema"
WSDL_NS = "http://schemas.xmlsoap.org/wsdl/"

NAMESPACES = {
    "xs": XS_NS,
    "wsdl": WSDL_NS,
}


def make_service(wsdl_path, **methods):
    """Create a minimal service object for WSDL parser tests."""
    namespace = SimpleNamespace(wsdl_path=str(wsdl_path))

    service = SimpleNamespace(
        operator=namespace,
        **methods,
    )

    return service


# pylint: disable=invalid-name
class TestGetMethodDocumentation:
    """Tests for extracting WSDL documentation and method parameters."""

    def test_returns_none_for_unknown_operation(self, tmp_path):
        """Test that an unknown operation returns None."""
        wsdl = tmp_path / "service.wsdl"
        wsdl.write_text(
            f"""
            <definitions
                xmlns="{WSDL_NS}"
                xmlns:tns="urn:test"
                targetNamespace="urn:test">
                <portType name="TestPort">
                    <operation name="KnownOperation"/>
                </portType>
            </definitions>
            """,
            encoding="utf-8",
        )

        service = make_service(
            wsdl,
            UnknownOperation=lambda value: value,
        )

        assert (
            get_method_documentation(
                service,
                "UnknownOperation",
            )
            is None
        )

    def test_extracts_documentation_and_parameters(self, tmp_path):
        """Test extracting operation documentation and method parameters."""
        wsdl = tmp_path / "service.wsdl"
        wsdl.write_text(
            f"""
            <definitions
                xmlns="{WSDL_NS}"
                xmlns:tns="urn:test"
                targetNamespace="urn:test">
                <portType name="TestPort">
                    <operation name="GetSomething">
                        <documentation>
                            Get something from the device.
                        </documentation>
                    </operation>
                </portType>
            </definitions>
            """,
            encoding="utf-8",
        )

        def GetSomething(required, optional="default"):
            """Test operation signature."""
            return required, optional

        service = make_service(
            wsdl,
            GetSomething=GetSomething,
        )

        result = get_method_documentation(
            service,
            "GetSomething",
        )

        assert result is not None
        assert "Get something from the device." in result["doc"]
        assert result["required"] == ["required"]
        assert result["optional"] == ["optional"]

    def test_handles_missing_wsdl(self, tmp_path):
        """Test fallback when the WSDL file does not exist."""
        service = make_service(
            tmp_path / "missing.wsdl",
            TestOperation=lambda value: value,
        )

        result = get_method_documentation(
            service,
            "TestOperation",
        )

        assert result is not None
        assert result["required"] == ["value"]
        assert result["optional"] == []

    def test_handles_method_without_parameters(self, tmp_path):
        """Test extracting a method with no arguments."""
        wsdl = tmp_path / "service.wsdl"
        wsdl.write_text(
            f"""
            <definitions
                xmlns="{WSDL_NS}"
                targetNamespace="urn:test">
                <portType name="TestPort">
                    <operation name="Ping">
                        <documentation>Ping the device.</documentation>
                    </operation>
                </portType>
            </definitions>
            """,
            encoding="utf-8",
        )

        def Ping():
            """Test operation without parameters."""
            return True

        service = make_service(wsdl, Ping=Ping)

        result = get_method_documentation(service, "Ping")

        assert result is not None
        assert result["required"] == []
        assert result["optional"] == []


class TestGetOperationTypeInfo:
    """Tests for extracting operation input and output message types."""

    def test_returns_none_for_unknown_operation(self, tmp_path):
        """Test that an unknown operation returns None."""
        wsdl = tmp_path / "service.wsdl"
        wsdl.write_text(
            f"""
            <definitions
                xmlns="{WSDL_NS}"
                targetNamespace="urn:test">
                <portType name="TestPort"/>
            </definitions>
            """,
            encoding="utf-8",
        )

        service = make_service(wsdl)

        assert (
            get_operation_type_info(
                service,
                "UnknownOperation",
            )
            is None
        )

    def test_extracts_input_and_output_messages(self, tmp_path):
        """Test extracting input and output message definitions."""
        wsdl = tmp_path / "service.wsdl"
        wsdl.write_text(
            f"""
            <definitions
                xmlns="{WSDL_NS}"
                xmlns:tns="urn:test"
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">

                <message name="TestRequest">
                    <part name="value" type="xs:string"/>
                </message>

                <message name="TestResponse">
                    <part name="result" type="xs:string"/>
                </message>

                <portType name="TestPort">
                    <operation name="TestOperation">
                        <input message="tns:TestRequest"/>
                        <output message="tns:TestResponse"/>
                    </operation>
                </portType>
            </definitions>
            """,
            encoding="utf-8",
        )

        service = make_service(wsdl)

        result = get_operation_type_info(
            service,
            "TestOperation",
        )

        assert result is not None
        assert result["input"] is not None
        assert result["output"] is not None

        assert result["input"]["name"] == "TestRequest"
        assert result["output"]["name"] == "TestResponse"

        assert result["input"]["parameters"][0]["name"] == "value"
        assert result["output"]["parameters"][0]["name"] == "result"

    def test_handles_operation_without_messages(self, tmp_path):
        """Test operations that do not define input or output messages."""
        wsdl = tmp_path / "service.wsdl"
        wsdl.write_text(
            f"""
            <definitions
                xmlns="{WSDL_NS}"
                targetNamespace="urn:test">
                <portType name="TestPort">
                    <operation name="TestOperation"/>
                </portType>
            </definitions>
            """,
            encoding="utf-8",
        )

        service = make_service(wsdl)

        result = get_operation_type_info(
            service,
            "TestOperation",
        )

        assert result == {
            "input": None,
            "output": None,
        }

    def test_handles_invalid_wsdl(self, tmp_path):
        """Test that malformed WSDL returns None."""
        wsdl = tmp_path / "invalid.wsdl"
        wsdl.write_text("<invalid", encoding="utf-8")

        service = make_service(wsdl)

        assert (
            get_operation_type_info(
                service,
                "TestOperation",
            )
            is None
        )


class TestParseMessageFromWsdl:
    """Tests for parsing WSDL message definitions."""

    def test_returns_empty_message_for_unknown_message(self):
        """Test parsing an unknown message name."""
        root = etree.fromstring(f"""
            <definitions
                xmlns="{WSDL_NS}"
                targetNamespace="urn:test"/>
            """.encode())

        result = parse_message_from_wsdl(
            root,
            "UnknownMessage",
            NAMESPACES,
            {
                "roots": [root],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert result == {
            "name": "UnknownMessage",
            "parameters": [],
        }

    def test_parses_direct_type_reference(self):
        """Test parsing a message part with a direct type reference."""
        root = etree.fromstring(f"""
            <definitions
                xmlns="{WSDL_NS}"
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">

                <message name="TestMessage">
                    <part name="value" type="xs:string"/>
                </message>
            </definitions>
            """.encode())

        result = parse_message_from_wsdl(
            root,
            "TestMessage",
            NAMESPACES,
            {
                "roots": [root],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert result["name"] == "TestMessage"
        assert len(result["parameters"]) == 1

        parameter = result["parameters"][0]

        assert parameter["name"] == "value"
        assert parameter["type"] == "string"
        assert parameter["minOccurs"] == "1"
        assert parameter["maxOccurs"] == "1"
        assert parameter["is_attribute"] is False

    def test_resolves_element_reference(self):
        """Test resolving a message part that references an element."""
        root = etree.fromstring(f"""
            <definitions
                xmlns="{WSDL_NS}"
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">

                <message name="TestMessage">
                    <part name="request" element="tns:Request"/>
                </message>

                <xs:schema
                    xmlns:tns="urn:test"
                    targetNamespace="urn:test">
                    <xs:element name="Request">
                        <xs:complexType>
                            <xs:sequence>
                                <xs:element name="Name" type="xs:string"/>
                            </xs:sequence>
                        </xs:complexType>
                    </xs:element>
                </xs:schema>
            </definitions>
            """.encode())

        namespaces = {
            **NAMESPACES,
            "tns": "urn:test",
        }

        result = parse_message_from_wsdl(
            root,
            "TestMessage",
            namespaces,
            {
                "roots": [root],
                "namespaces": namespaces,
                "wsdl_dir": ".",
            },
        )

        assert result["name"] == "TestMessage"
        assert result["parameters"]

        assert result["parameters"][0]["name"] == "Name"


class TestCleanDocumentationHtml:
    """Tests for cleaning HTML from WSDL documentation."""

    def test_empty_text(self):
        """Test that empty documentation remains empty."""
        assert clean_documentation_html("") == ""
        assert clean_documentation_html(None) is None

    def test_removes_html_tags(self):
        """Test removing HTML tags from documentation."""
        result = clean_documentation_html("<p>Hello <strong>world</strong></p>")

        assert result == "Hello world"

    def test_converts_links(self):
        """Test converting HTML links into readable text."""
        result = clean_documentation_html('<a href="https://example.com">Example</a>')

        assert result == "Example (https://example.com)"

    def test_keeps_url_without_link_text(self):
        """Test preserving URLs when a link has no visible text."""
        result = clean_documentation_html('<a href="https://example.com"></a>')

        assert result == "https://example.com"

    def test_normalizes_whitespace(self):
        """Test collapsing repeated whitespace."""
        result = clean_documentation_html("Hello\n\n   world\tfrom parser")

        assert result == "Hello world from parser"

    def test_handles_multiline_links(self):
        """Test converting links whose content spans multiple lines."""
        result = clean_documentation_html("""
            <a href="https://example.com">
                Example
            </a>
            """)

        assert result == "Example (https://example.com)"


class TestExtractDocumentationText:
    """Tests for extracting text from XML documentation elements."""

    def test_none_element(self):
        """Test extracting text from a missing element."""
        assert extract_documentation_text(None) == ""

    def test_text_only(self):
        """Test extracting plain documentation text."""
        element = etree.fromstring(b"<documentation>Hello world</documentation>")

        assert extract_documentation_text(element) == "Hello world"

    def test_text_and_children(self):
        """Test extracting text before, inside, and after child elements."""
        element = etree.fromstring(b"""
            <documentation>
                Before
                <b>middle</b>
                After
            </documentation>
            """)

        result = extract_documentation_text(element)

        assert "Before" in result
        assert "middle" in result
        assert "After" in result


class TestLoadImportedSchemas:
    """Tests for loading imported and included XML schemas."""

    def test_loads_imported_schema(self, tmp_path):
        """Test loading a local imported schema into the context."""
        imported = tmp_path / "imported.xsd"
        imported.write_text(
            f"""
            <xs:schema
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:imported">
                <xs:element name="ImportedElement" type="xs:string"/>
            </xs:schema>
            """,
            encoding="utf-8",
        )

        root = etree.fromstring(f"""
            <definitions
                xmlns="{WSDL_NS}"
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">
                <xs:schema targetNamespace="urn:test">
                    <xs:import
                        namespace="urn:imported"
                        schemaLocation="imported.xsd"/>
                </xs:schema>
            </definitions>
            """.encode())

        context = {
            "roots": [root],
            "namespaces": NAMESPACES,
            "wsdl_dir": str(tmp_path),
        }

        _load_imported_schemas(
            root,
            context,
            NAMESPACES,
        )

        assert len(context["roots"]) == 2

        imported_root = context["roots"][1]

        assert (
            imported_root.find(
                ".//xs:element[@name='ImportedElement']",
                NAMESPACES,
            )
            is not None
        )

    def test_loads_included_schema(self, tmp_path):
        """Test loading a local included schema into the context."""
        included = tmp_path / "included.xsd"
        included.write_text(
            f"""
            <xs:schema
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">
                <xs:element name="IncludedElement" type="xs:string"/>
            </xs:schema>
            """,
            encoding="utf-8",
        )

        root = etree.fromstring(f"""
            <definitions
                xmlns="{WSDL_NS}"
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">
                <xs:schema targetNamespace="urn:test">
                    <xs:include schemaLocation="included.xsd"/>
                </xs:schema>
            </definitions>
            """.encode())

        context = {
            "roots": [root],
            "namespaces": NAMESPACES,
            "wsdl_dir": str(tmp_path),
        }

        _load_imported_schemas(
            root,
            context,
            NAMESPACES,
        )

        assert len(context["roots"]) == 2


class TestResolveElementType:
    """Tests for recursively resolving XML schema elements."""

    def test_returns_empty_for_unknown_element(self):
        """Test resolving an element that does not exist."""
        root = etree.fromstring(f"""
            <xs:schema
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test"/>
            """.encode())

        result = resolve_element_type(
            "Unknown",
            NAMESPACES,
            {
                "roots": [root],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert not result

    def test_resolves_simple_sequence(self):
        """Test resolving elements from a simple complex type sequence."""
        root = etree.fromstring(f"""
            <xs:schema
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">

                <xs:element name="Request">
                    <xs:complexType>
                        <xs:sequence>
                            <xs:element
                                name="Name"
                                type="xs:string"/>
                            <xs:element
                                name="Count"
                                type="xs:int"
                                minOccurs="0"
                                maxOccurs="unbounded"/>
                        </xs:sequence>
                    </xs:complexType>
                </xs:element>

            </xs:schema>
            """.encode())

        result = resolve_element_type(
            "Request",
            NAMESPACES,
            {
                "roots": [root],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert [item["name"] for item in result] == [
            "Name",
            "Count",
        ]

        assert result[0]["type"] == "string"
        assert result[0]["is_attribute"] is False

        assert result[1]["minOccurs"] == "0"
        assert result[1]["maxOccurs"] == "unbounded"

    def test_resolves_attributes(self):
        """Test extracting attributes from a complex type."""
        root = etree.fromstring(f"""
            <xs:schema
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">

                <xs:element name="Request">
                    <xs:complexType>
                        <xs:attribute
                            name="id"
                            type="xs:string"
                            use="required"/>
                    </xs:complexType>
                </xs:element>

            </xs:schema>
            """.encode())

        result = resolve_element_type(
            "Request",
            NAMESPACES,
            {
                "roots": [root],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert len(result) == 1
        assert result[0]["name"] == "id"
        assert result[0]["type"] == "string"
        assert result[0]["is_attribute"] is True
        assert result[0]["minOccurs"] == "1"

    def test_respects_recursion_limit(self):
        """Test that excessive recursion returns an empty result."""
        root = etree.fromstring(f"""
            <xs:schema
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">
                <xs:element name="Request" type="RequestType"/>
                <xs:complexType name="RequestType">
                    <xs:sequence>
                        <xs:element name="Value" type="xs:string"/>
                    </xs:sequence>
                </xs:complexType>
            </xs:schema>
            """.encode())

        result = resolve_element_type(
            "Request",
            NAMESPACES,
            {
                "roots": [root],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
            depth=11,
        )

        assert not result


class TestResolveComplexType:
    """Tests for resolving named XML schema complex types."""

    def test_returns_empty_for_unknown_type(self):
        """Test resolving a complex type that does not exist."""
        root = etree.fromstring(f"""
            <xs:schema
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test"/>
            """.encode())

        result = resolve_complex_type(
            "UnknownType",
            NAMESPACES,
            {
                "roots": [root],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert not result

    def test_resolves_sequence(self):
        """Test extracting children from a named complex type."""
        root = etree.fromstring(f"""
            <xs:schema
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">

                <xs:complexType name="RequestType">
                    <xs:sequence>
                        <xs:element
                            name="Name"
                            type="xs:string"/>
                        <xs:element
                            name="Enabled"
                            type="xs:boolean"
                            minOccurs="0"/>
                    </xs:sequence>
                </xs:complexType>

            </xs:schema>
            """.encode())

        result = resolve_complex_type(
            "RequestType",
            NAMESPACES,
            {
                "roots": [root],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert [item["name"] for item in result] == [
            "Name",
            "Enabled",
        ]

        assert result[1]["minOccurs"] == "0"

    def test_resolves_attributes(self):
        """Test extracting attributes from a named complex type."""
        root = etree.fromstring(f"""
            <xs:schema
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">

                <xs:complexType name="RequestType">
                    <xs:attribute
                        name="token"
                        type="xs:string"
                        use="required"/>
                </xs:complexType>

            </xs:schema>
            """.encode())

        result = resolve_complex_type(
            "RequestType",
            NAMESPACES,
            {
                "roots": [root],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert result[0]["name"] == "token"
        assert result[0]["is_attribute"] is True
        assert result[0]["minOccurs"] == "1"

    def test_resolves_base_type(self):
        """Test resolving children inherited through complex type extension."""
        root = etree.fromstring(f"""
            <xs:schema
                xmlns:xs="{XS_NS}"
                targetNamespace="urn:test">

                <xs:complexType name="BaseType">
                    <xs:sequence>
                        <xs:element name="BaseValue" type="xs:string"/>
                    </xs:sequence>
                </xs:complexType>

                <xs:complexType name="ExtendedType">
                    <xs:complexContent>
                        <xs:extension base="BaseType">
                            <xs:sequence>
                                <xs:element
                                    name="ExtendedValue"
                                    type="xs:int"/>
                            </xs:sequence>
                        </xs:extension>
                    </xs:complexContent>
                </xs:complexType>

            </xs:schema>
            """.encode())

        result = resolve_complex_type(
            "ExtendedType",
            NAMESPACES,
            {
                "roots": [root],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        names = [item["name"] for item in result]

        assert "BaseValue" in names
        assert "ExtendedValue" in names


class TestParseInlineComplexType:
    """Tests for parsing inline XML schema complex types."""

    def test_empty_complex_type(self):
        """Test parsing an empty inline complex type."""
        complex_type = etree.fromstring(f"""
            <xs:complexType xmlns:xs="{XS_NS}"/>
            """.encode())

        result = parse_inline_complex_type(
            complex_type,
            NAMESPACES,
            {
                "roots": [complex_type],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert not result

    def test_parses_sequence(self):
        """Test parsing elements from an inline sequence."""
        complex_type = etree.fromstring(f"""
            <xs:complexType xmlns:xs="{XS_NS}">
                <xs:sequence>
                    <xs:element
                        name="Name"
                        type="xs:string"/>
                    <xs:element
                        name="Count"
                        type="xs:int"
                        minOccurs="0"/>
                </xs:sequence>
            </xs:complexType>
            """.encode())

        result = parse_inline_complex_type(
            complex_type,
            NAMESPACES,
            {
                "roots": [complex_type],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert [item["name"] for item in result] == [
            "Name",
            "Count",
        ]

        assert result[1]["minOccurs"] == "0"

    def test_parses_attributes(self):
        """Test parsing attributes from an inline complex type."""
        complex_type = etree.fromstring(f"""
            <xs:complexType xmlns:xs="{XS_NS}">
                <xs:attribute
                    name="id"
                    type="xs:string"
                    use="required"/>
            </xs:complexType>
            """.encode())

        result = parse_inline_complex_type(
            complex_type,
            NAMESPACES,
            {
                "roots": [complex_type],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert len(result) == 1
        assert result[0]["name"] == "id"
        assert result[0]["is_attribute"] is True
        assert result[0]["minOccurs"] == "1"

    def test_parses_nested_inline_type(self):
        """Test parsing a nested inline complex type."""
        complex_type = etree.fromstring(f"""
            <xs:complexType xmlns:xs="{XS_NS}">
                <xs:sequence>
                    <xs:element name="Parent">
                        <xs:complexType>
                            <xs:sequence>
                                <xs:element
                                    name="Child"
                                    type="xs:string"/>
                            </xs:sequence>
                        </xs:complexType>
                    </xs:element>
                </xs:sequence>
            </xs:complexType>
            """.encode())

        result = parse_inline_complex_type(
            complex_type,
            NAMESPACES,
            {
                "roots": [complex_type],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
        )

        assert len(result) == 1
        assert result[0]["name"] == "Parent"
        assert result[0]["children"]

        assert result[0]["children"][0]["name"] == "Child"

    def test_respects_recursion_limit(self):
        """Test that deeply nested inline types stop at the recursion limit."""
        complex_type = etree.fromstring(f"""
            <xs:complexType xmlns:xs="{XS_NS}">
                <xs:sequence>
                    <xs:element name="Value" type="xs:string"/>
                </xs:sequence>
            </xs:complexType>
            """.encode())

        result = parse_inline_complex_type(
            complex_type,
            NAMESPACES,
            {
                "roots": [complex_type],
                "namespaces": NAMESPACES,
                "wsdl_dir": ".",
            },
            depth=11,
        )

        assert not result
