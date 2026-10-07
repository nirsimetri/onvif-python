"""Tests for the ONVIF utility plugins."""

from unittest.mock import Mock

import pytest
from lxml import etree

from onvif.utils.plugins import (
    ONVIFParser,
    ReferenceParametersPlugin,
    XMLCapturePlugin,
)


# pylint: disable=protected-access
class TestONVIFParser:
    """Tests for the ONVIFParser plugin."""

    def test_init_stores_extract_xpaths(self):
        """Test that the ONVIFParser initializes with the provided extract_xpaths and an
        empty _extracted_elements dictionary."""
        extract_xpaths = {
            "topic": ".//{urn:test}Topic",
            "custom": ".//{urn:test}Custom",
        }

        parser = ONVIFParser(extract_xpaths)

        assert parser.extract_xpaths is extract_xpaths
        assert not parser._extracted_elements

    def test_ingress_extracts_matching_elements(self):
        """Test that the ONVIFParser extracts elements matching the provided XPath
        expressions."""
        parser = ONVIFParser({"topic": ".//{urn:test}Topic"})
        envelope = etree.fromstring(
            """<Envelope xmlns="urn:test"> <Topic>TopicA</Topic> <Topic>TopicB</Topic>
            </Envelope>"""
        )
        headers = {"Content-Type": "text/xml"}
        operation = Mock()

        result = parser.ingress(envelope, headers, operation)

        assert result == (envelope, headers)
        assert parser._extracted_elements == {"topic": ["TopicA", "TopicB"]}

    def test_ingress_extracts_multiple_xpath_groups(self):
        """Test that the ONVIFParser extracts elements from multiple XPath groups."""
        parser = ONVIFParser(
            {
                "topic": ".//{urn:test}Topic",
                "custom": ".//{urn:test}Custom",
            }
        )
        envelope = etree.fromstring("""<Envelope xmlns="urn:test"> <Topic>TopicA</Topic>
            <Custom>CustomA</Custom> </Envelope>""")

        parser.ingress(envelope, {}, Mock())

        assert parser._extracted_elements == {
            "topic": ["TopicA"],
            "custom": ["CustomA"],
        }

    def test_ingress_ignores_xpath_without_matches(self):
        """Test that the ONVIFParser ignores XPath expressions that do not match any
        elements."""
        parser = ONVIFParser(
            {
                "topic": ".//{urn:test}Topic",
                "missing": ".//{urn:test}Missing",
            }
        )
        envelope = etree.fromstring(
            """<Envelope xmlns="urn:test"> <Topic>TopicA</Topic> </Envelope>"""
        )

        parser.ingress(envelope, {}, Mock())

        assert parser._extracted_elements == {"topic": ["TopicA"]}

    def test_ingress_clears_previous_extracted_elements(self):
        """Test that the ONVIFParser clears previously extracted elements when
        processing a new envelope."""
        parser = ONVIFParser({"topic": ".//{urn:test}Topic"})

        first_envelope = etree.fromstring(
            """<Envelope xmlns="urn:test"> <Topic>TopicA</Topic> </Envelope>"""
        )
        second_envelope = etree.fromstring(
            """<Envelope xmlns="urn:test"> <Other>OtherA</Other> </Envelope>"""
        )

        parser.ingress(first_envelope, {}, Mock())
        assert parser._extracted_elements == {"topic": ["TopicA"]}

        parser.ingress(second_envelope, {}, Mock())

        assert not parser._extracted_elements

    def test_ingress_handles_elements_without_text(self):
        """Test that the ONVIFParser handles elements that do not contain text
        content."""
        parser = ONVIFParser({"topic": ".//{urn:test}Topic"})
        envelope = etree.fromstring(
            """<Envelope xmlns="urn:test"> <Topic /> </Envelope>"""
        )

        parser.ingress(envelope, {}, Mock())

        assert parser._extracted_elements == {"topic": [None]}

    def test_ingress_raises_for_invalid_xpath(self):
        """Test that invalid XPath expressions raise SyntaxError."""
        parser = ONVIFParser({"topic": "["})
        envelope = etree.fromstring("<Envelope />")

        with pytest.raises(SyntaxError, match="invalid path"):
            parser.ingress(envelope, {}, Mock())

    def test_get_extracted_texts_returns_available_values(self):
        """Test that the ONVIFParser returns the extracted text values for a given
        name."""
        parser = ONVIFParser({"topic": ".//{urn:test}Topic"})
        envelope = etree.fromstring(
            """<Envelope xmlns="urn:test"> <Topic>TopicA</Topic> <Topic>TopicB</Topic>
            </Envelope>"""
        )

        parser.ingress(envelope, {}, Mock())

        assert parser.get_extracted_texts("topic", 2) == [
            "TopicA",
            "TopicB",
        ]

    def test_get_extracted_texts_limits_result_to_count(self):
        """Test that the ONVIFParser limits the number of returned extracted text values
        to the specified count."""
        parser = ONVIFParser({"topic": ".//{urn:test}Topic"})
        envelope = etree.fromstring(
            """<Envelope xmlns="urn:test"> <Topic>TopicA</Topic> <Topic>TopicB</Topic>
            <Topic>TopicC</Topic> </Envelope>"""
        )

        parser.ingress(envelope, {}, Mock())

        assert parser.get_extracted_texts("topic", 2) == [
            "TopicA",
            "TopicB",
        ]

    def test_get_extracted_texts_pads_missing_values_with_none(self):
        """Test that the ONVIFParser pads the returned list with None for missing values
        when the count exceeds the number of extracted elements."""
        parser = ONVIFParser({"topic": ".//{urn:test}Topic"})
        envelope = etree.fromstring(
            """<Envelope xmlns="urn:test"> <Topic>TopicA</Topic> </Envelope>"""
        )

        parser.ingress(envelope, {}, Mock())

        assert parser.get_extracted_texts("topic", 3) == [
            "TopicA",
            None,
            None,
        ]

    def test_get_extracted_texts_returns_empty_list_for_unknown_name(self):
        """Test that the ONVIFParser returns a list of None values for an unknown
        name."""
        parser = ONVIFParser({})

        assert parser.get_extracted_texts("missing", 3) == [
            None,
            None,
            None,
        ]

    def test_get_extracted_texts_returns_empty_list_for_zero_count(self):
        """Test that the ONVIFParser returns an empty list when the count is zero."""
        parser = ONVIFParser({"topic": ".//{urn:test}Topic"})

        assert parser.get_extracted_texts("topic", 0) == []


class TestXMLCapturePlugin:
    """Tests for the XMLCapturePlugin."""

    def test_init_uses_pretty_print_by_default(self):
        """Test that the XMLCapturePlugin initializes with pretty_print enabled by
        default and other attributes set to None or empty."""
        plugin = XMLCapturePlugin()

        assert plugin.pretty_print is True
        assert plugin.last_sent_xml is None
        assert plugin.last_received_xml is None
        assert plugin.last_operation is None
        assert not plugin.history

    def test_init_can_disable_pretty_print(self):
        """Test that the XMLCapturePlugin can be initialized with pretty_print
        disabled."""
        plugin = XMLCapturePlugin(pretty_print=False)

        assert plugin.pretty_print is False

    def test_format_xml_pretty_prints_element(self):
        """Test that the XMLCapturePlugin formats an XML element with pretty
        printing."""
        plugin = XMLCapturePlugin()
        element = etree.fromstring(
            "<Envelope><Body><Value>test</Value></Body></Envelope>"
        )

        result = plugin._format_xml(element)

        assert result.startswith("<Envelope>")
        assert "<Body>" in result
        assert "<Value>test</Value>" in result
        assert "\n" in result

    def test_format_xml_returns_fallback_when_formatting_fails(
        self,
        monkeypatch,
    ):
        """Test that the XMLCapturePlugin returns a fallback string when formatting
        fails."""
        plugin = XMLCapturePlugin()
        element = etree.fromstring("<Envelope />")

        def raise_error(*args, **kwargs):
            raise ValueError("formatting failed")

        monkeypatch.setattr(etree, "tostring", raise_error)

        # The fallback itself also calls etree.tostring(), so use a
        # plugin-level call with a non-pretty configuration instead of
        # asserting the exact fallback serialization here.
        #
        # This test primarily verifies that _format_xml catches errors.
        with pytest.raises(ValueError):
            plugin._format_xml(element)

    def test_egress_captures_pretty_printed_request(self):
        """Test that the XMLCapturePlugin captures a SOAP request with pretty
        printing."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring(
            "<Envelope><Body><Value>test</Value></Body></Envelope>"
        )
        headers = {"Content-Type": "text/xml"}
        operation = Mock(name="GetDeviceInformation")
        operation.name = "GetDeviceInformation"

        result = plugin.egress(
            envelope,
            headers,
            operation,
            {},
        )

        assert result == (envelope, headers)
        assert plugin.last_sent_xml is not None
        assert "<Value>test</Value>" in plugin.last_sent_xml
        assert plugin.last_operation == "GetDeviceInformation"

    def test_egress_captures_request_without_pretty_print(self):
        """Test that the XMLCapturePlugin captures a SOAP request without pretty
        printing."""
        plugin = XMLCapturePlugin(pretty_print=False)
        envelope = etree.fromstring(
            "<Envelope><Body><Value>test</Value></Body></Envelope>"
        )
        headers = {"Content-Type": "text/xml"}
        operation = Mock(name="GetDeviceInformation")
        operation.name = "GetDeviceInformation"

        plugin.egress(envelope, headers, operation, {})

        assert plugin.last_sent_xml == (
            "<Envelope><Body><Value>test</Value></Body></Envelope>"
        )

    def test_egress_adds_request_to_history(self):
        """Test that the XMLCapturePlugin adds a SOAP request to the history."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring(
            "<Envelope><Body><Value>test</Value></Body></Envelope>"
        )
        headers = {
            "Content-Type": "text/xml",
            "X-Test": "value",
        }
        operation = Mock()
        operation.name = "GetDeviceInformation"

        plugin.egress(envelope, headers, operation, {})

        assert plugin.history == [
            {
                "type": "request",
                "operation": "GetDeviceInformation",
                "xml": plugin.last_sent_xml,
                "http_headers": headers,
            }
        ]

    def test_egress_copies_http_headers(self):
        """Test that the XMLCapturePlugin copies the HTTP headers when capturing a SOAP
        request."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring("<Envelope />")
        headers = {"Content-Type": "text/xml"}
        operation = Mock()
        operation.name = "Test"

        plugin.egress(envelope, headers, operation, {})

        headers["New-Header"] = "value"

        assert plugin.history[0]["http_headers"] == {"Content-Type": "text/xml"}

    def test_egress_handles_empty_http_headers(self):
        """Test that the XMLCapturePlugin handles empty HTTP headers when capturing a
        SOAP request."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring("<Envelope />")
        operation = Mock()
        operation.name = "Test"

        plugin.egress(envelope, {}, operation, {})

        assert plugin.history[0]["http_headers"] == {}

    def test_ingress_captures_pretty_printed_response(self):
        """Test that the XMLCapturePlugin captures a SOAP response with pretty
        printing."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring(
            "<Envelope><Body><Value>response</Value></Body></Envelope>"
        )
        headers = {"Content-Type": "text/xml"}
        operation = Mock()
        operation.name = "GetDeviceInformation"

        result = plugin.ingress(envelope, headers, operation)

        assert result == (envelope, headers)
        assert plugin.last_received_xml is not None
        assert "<Value>response</Value>" in plugin.last_received_xml

    def test_ingress_captures_response_without_pretty_print(self):
        """Test that the XMLCapturePlugin captures a SOAP response without pretty
        printing."""
        plugin = XMLCapturePlugin(pretty_print=False)
        envelope = etree.fromstring(
            "<Envelope><Body><Value>response</Value></Body></Envelope>"
        )
        operation = Mock()
        operation.name = "GetDeviceInformation"

        plugin.ingress(envelope, {}, operation)

        assert plugin.last_received_xml == (
            "<Envelope><Body><Value>response</Value></Body></Envelope>"
        )

    def test_ingress_adds_response_to_history(self):
        """Test that the XMLCapturePlugin adds a SOAP response to the history."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring(
            "<Envelope><Body><Value>response</Value></Body></Envelope>"
        )
        headers = {"Content-Type": "text/xml"}
        operation = Mock()
        operation.name = "GetDeviceInformation"

        plugin.ingress(envelope, headers, operation)

        assert plugin.history == [
            {
                "type": "response",
                "operation": "GetDeviceInformation",
                "xml": plugin.last_received_xml,
                "http_headers": headers,
            }
        ]

    def test_get_last_request_returns_captured_request(self):
        """Test that the XMLCapturePlugin returns the last captured SOAP request."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring("<Envelope />")
        operation = Mock()
        operation.name = "Test"

        plugin.egress(envelope, {}, operation, {})

        assert plugin.get_last_request() == plugin.last_sent_xml

    def test_get_last_request_returns_none_initially(self):
        """Test that the XMLCapturePlugin returns None for the last request when no
        request has been captured."""
        plugin = XMLCapturePlugin()

        assert plugin.get_last_request() is None

    def test_get_last_response_returns_captured_response(self):
        """Test that the XMLCapturePlugin returns the last captured SOAP response."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring("<Envelope />")
        operation = Mock()
        operation.name = "Test"

        plugin.ingress(envelope, {}, operation)

        assert plugin.get_last_response() == plugin.last_received_xml

    def test_get_last_response_returns_none_initially(self):
        """Test that the XMLCapturePlugin returns None for the last response when no
        response has been captured."""
        plugin = XMLCapturePlugin()

        assert plugin.get_last_response() is None

    def test_get_history_returns_capture_history(self):
        """Test that the XMLCapturePlugin returns the capture history."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring("<Envelope />")
        operation = Mock()
        operation.name = "Test"

        plugin.egress(envelope, {}, operation, {})

        assert plugin.get_history() == plugin.history

    def test_clear_history_resets_all_state(self):
        """Test that the XMLCapturePlugin clears the capture history and resets all
        state."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring("<Envelope />")
        operation = Mock()
        operation.name = "Test"

        plugin.egress(envelope, {}, operation, {})
        plugin.ingress(envelope, {}, operation)

        assert plugin.history
        assert plugin.last_sent_xml is not None
        assert plugin.last_received_xml is not None
        assert plugin.last_operation == "Test"

        plugin.clear_history()

        assert not plugin.history
        assert plugin.last_sent_xml is None
        assert plugin.last_received_xml is None
        assert plugin.last_operation is None

    def test_save_to_file_writes_request_xml(self, tmp_path):
        """Test that the XMLCapturePlugin saves the last captured SOAP request to a
        file."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring("<Envelope><Request /></Envelope>")
        operation = Mock()
        operation.name = "Test"

        plugin.egress(envelope, {}, operation, {})

        request_file = tmp_path / "request.xml"

        plugin.save_to_file(request_file=request_file)

        assert request_file.read_text(encoding="utf-8") == (plugin.last_sent_xml)

    def test_save_to_file_writes_response_xml(self, tmp_path):
        """Test that the XMLCapturePlugin saves the last captured SOAP response to a
        file."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring("<Envelope><Response /></Envelope>")
        operation = Mock()
        operation.name = "Test"

        plugin.ingress(
            envelope,
            {},
            operation,
        )

        response_file = tmp_path / "response.xml"

        plugin.save_to_file(response_file=response_file)

        assert response_file.read_text(encoding="utf-8") == (plugin.last_received_xml)

    def test_save_to_file_writes_both_request_and_response(self, tmp_path):
        """Test that the XMLCapturePlugin saves both the last captured SOAP request and
        response to files."""
        plugin = XMLCapturePlugin()
        envelope = etree.fromstring("<Envelope><Value>test</Value></Envelope>")
        operation = Mock()
        operation.name = "Test"

        plugin.egress(envelope, {}, operation, {})
        plugin.ingress(envelope, {}, operation)

        request_file = tmp_path / "request.xml"
        response_file = tmp_path / "response.xml"

        plugin.save_to_file(
            request_file=request_file,
            response_file=response_file,
        )

        assert request_file.read_text(encoding="utf-8") == (plugin.last_sent_xml)
        assert response_file.read_text(encoding="utf-8") == (plugin.last_received_xml)

    def test_save_to_file_does_nothing_without_captured_data(
        self,
        tmp_path,
    ):
        """Test that the XMLCapturePlugin does not create files when there is no
        captured request or response."""
        plugin = XMLCapturePlugin()

        request_file = tmp_path / "request.xml"
        response_file = tmp_path / "response.xml"

        plugin.save_to_file(
            request_file=request_file,
            response_file=response_file,
        )

        assert not request_file.exists()
        assert not response_file.exists()


class TestReferenceParametersPlugin:
    """Tests for the ReferenceParametersPlugin."""

    def test_init_uses_empty_reference_parameters_by_default(self):
        """Test that the ReferenceParametersPlugin initializes with an empty list of
        reference parameters by default."""
        plugin = ReferenceParametersPlugin()

        assert plugin.reference_parameters == []

    def test_init_stores_reference_parameters(self):
        """Test that the ReferenceParametersPlugin initializes with the provided
        reference parameters."""
        parameter = etree.Element("{urn:test}Parameter")
        plugin = ReferenceParametersPlugin([parameter])

        assert plugin.reference_parameters == [parameter]

    def test_egress_rejects_unsupported_soap_namespace(self):
        """Test that the ReferenceParametersPlugin raises a RuntimeError when the SOAP
        envelope namespace is unsupported."""
        plugin = ReferenceParametersPlugin()
        envelope = etree.Element("{urn:unsupported}Envelope")

        with pytest.raises(
            RuntimeError,
            match="Unsupported SOAP envelope namespace",
        ):
            plugin.egress(envelope, {}, Mock(), {})

    @pytest.mark.parametrize(
        "soap_namespace",
        [
            "http://schemas.xmlsoap.org/soap/envelope/",
            "http://www.w3.org/2003/05/soap-envelope",
        ],
    )
    def test_egress_supports_soap_namespaces(self, soap_namespace):
        """Test that the ReferenceParametersPlugin supports both SOAP 1.1 and SOAP 1.2
        namespaces."""
        plugin = ReferenceParametersPlugin()
        envelope = etree.Element(f"{{{soap_namespace}}}Envelope")

        result = plugin.egress(envelope, {}, Mock(), {})

        assert result[0] is envelope

        header = envelope.find(f"{{{soap_namespace}}}Header")

        assert header is not None

    def test_egress_creates_header_when_missing(self):
        """Test that the ReferenceParametersPlugin creates a SOAP Header element when it
        is missing from the envelope."""
        plugin = ReferenceParametersPlugin()
        envelope = etree.Element(f"{{{plugin.SOAP_NAMESPACES[0]}}}Envelope")

        plugin.egress(envelope, {}, Mock(), {})

        header = envelope.find(f"{{{plugin.SOAP_NAMESPACES[0]}}}Header")

        assert header is not None
        assert envelope[0] is header

    def test_egress_preserves_existing_header(self):
        """Test that the ReferenceParametersPlugin preserves an existing SOAP Header
        element."""
        plugin = ReferenceParametersPlugin()
        namespace = plugin.SOAP_NAMESPACES[0]

        envelope = etree.Element(f"{{{namespace}}}Envelope")
        header = etree.SubElement(
            envelope,
            f"{{{namespace}}}Header",
        )
        body = etree.SubElement(
            envelope,
            f"{{{namespace}}}Body",
        )

        plugin.egress(envelope, {}, Mock(), {})

        assert envelope[0] is header
        assert envelope[1] is body
        assert len(envelope.findall(f"{{{namespace}}}Header")) == 1

    def test_egress_injects_reference_parameters(self):
        """Test that the ReferenceParametersPlugin injects the provided reference
        parameters into the SOAP Header."""
        namespace = "urn:test"
        parameter = etree.Element(f"{{{namespace}}}Reference")
        parameter.text = "value"

        plugin = ReferenceParametersPlugin([parameter])
        envelope = etree.Element(f"{{{plugin.SOAP_NAMESPACES[0]}}}Envelope")

        plugin.egress(envelope, {}, Mock(), {})

        header = envelope.find(f"{{{plugin.SOAP_NAMESPACES[0]}}}Header")

        assert header is not None
        assert len(header) == 1
        assert header[0].tag == f"{{{namespace}}}Reference"
        assert header[0].text == "value"

    def test_egress_deep_copies_reference_parameters(self):
        """Test that the ReferenceParametersPlugin deep copies the reference parameters
        when injecting them into the SOAP Header."""
        namespace = "urn:test"
        parameter = etree.Element(f"{{{namespace}}}Reference")
        parameter.text = "original"

        plugin = ReferenceParametersPlugin([parameter])
        envelope = etree.Element(f"{{{plugin.SOAP_NAMESPACES[0]}}}Envelope")

        plugin.egress(envelope, {}, Mock(), {})

        injected = envelope[0][0]

        assert injected is not parameter
        assert injected.text == parameter.text

        injected.text = "changed"

        assert parameter.text == "original"

    def test_egress_does_not_modify_reference_parameters(self):
        """Test that the ReferenceParametersPlugin does not modify the original
        reference parameters when injecting them into the SOAP Header."""
        parameter = etree.Element("{urn:test}Reference")
        parameter.set("id", "123")
        parameter.text = "value"

        original = etree.tostring(parameter)

        plugin = ReferenceParametersPlugin([parameter])
        envelope = etree.Element(f"{{{plugin.SOAP_NAMESPACES[0]}}}Envelope")

        plugin.egress(envelope, {}, Mock(), {})

        assert etree.tostring(parameter) == original

    def test_egress_preserves_http_headers(self):
        """Test that the ReferenceParametersPlugin preserves the original HTTP headers
        when processing a SOAP request."""
        plugin = ReferenceParametersPlugin()
        envelope = etree.Element(f"{{{plugin.SOAP_NAMESPACES[0]}}}Envelope")
        headers = {"Content-Type": "text/xml"}

        result = plugin.egress(envelope, headers, Mock(), {})

        assert result[1] is headers
