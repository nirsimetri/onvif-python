"""Auxiliary custom Zeep plugins outside the core scope.

All classes in this module inherit from Zeep's Plugin (`zeep.plugins`) class.
"""

from __future__ import annotations

import logging
from copy import deepcopy
from typing import Any

from lxml import etree
from zeep import Plugin

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ONVIFParser(Plugin):
    """Lightweight Zeep plugin for extracting XML elements from SOAP responses.

    The parser extracts text from XML elements matching configured XPath
    expressions before Zeep parses the SOAP response. This is useful for
    extracting elements that Zeep does not parse correctly, such as
    `simpleContent` elements with attributes.

    Args:
        extract_xpaths: Dictionary mapping extraction names to XPath expressions.

    Attributes:
        extract_xpaths: XPath expressions used to extract elements from SOAP
            responses.
        _extracted_elements: Extracted element texts from the most recent SOAP
            response, grouped by extraction name.

    !!! tip "Version History"
        - Available since [`>=v0.2.2`](/onvif-python/releases/#v0.2.2).

    ??? example "Usage"
        ```python linenums="1"
        from onvif import ONVIFClient, ONVIFParser

        parser = ONVIFParser({
            "topic": ".//{http://docs.oasis-open.org/wsn/b-2}Topic",
        })

        client = ONVIFClient(
            host, port, username, password, plugins=[parser]
        )

        subscription = client.events().CreatePullPointSubscription()
        pullpoint = client.pullpoint(subscription)

        msgs = pullpoint.PullMessages(
            Timeout="PT5S",
            MessageLimit=10,
        )

        topics = parser.get_extracted_texts(
            "topic",
            len(msgs.NotificationMessage),
        )
        ```

    ??? note "Notes"
        - Uses Zeep's `ingress()` hook to access the raw SOAP response.
        - The extraction cache is cleared before each SOAP response.
        - Supports any XPath expression accepted by `lxml`.
    """

    def __init__(self, extract_xpaths: dict[str, str]):
        """Initialize XML element parser.

        Args:
            extract_xpaths: Dictionary mapping names to XPath expressions.
                            XPath expressions will be used to find elements in SOAP response.

        Example:
            ```python
            {
                'topic': './/{http://docs.oasis-open.org/wsn/b-2}Topic',
                'custom': './/ns:CustomElement'
            }
            ```
        """
        self.extract_xpaths: dict[str, str] = extract_xpaths
        self._extracted_elements: dict[str, list[str | None]] = {}

        logger.debug(
            "ONVIFParser initialized with XPaths: %s", list(extract_xpaths.keys())
        )

    def ingress(
        self, envelope: etree._Element, http_headers: dict[str, str], operation: Any
    ):
        """Process a SOAP response before Zeep deserializes it.

        This Zeep ``ingress`` hook inspects the raw SOAP response envelope and
        extracts text from elements matching the configured XPath expressions.
        The extracted values are stored temporarily and can be retrieved with
        `get_extracted_texts`.

        The extraction cache is cleared before processing each response, so it
        always contains values from the most recently processed SOAP response.

        Args:
            envelope: Raw SOAP response envelope as an `lxml.etree.Element`.
            http_headers: HTTP response headers returned by the device.
            operation: Zeep operation associated with the SOAP response.

        Returns:
            A tuple containing the unchanged ``envelope`` and ``http_headers``.
                Returning both values allows Zeep to continue processing the response
                and allows other plugins in the chain to process it as well.
        """
        # Auto-clear cache from previous response
        self._extracted_elements = {}

        try:
            # Extract elements using XPath from raw XML envelope
            for name, xpath in self.extract_xpaths.items():
                elements = envelope.findall(xpath)

                # Extract text content from found elements
                texts = [elem.text for elem in elements]

                if texts:
                    self._extracted_elements[name] = texts
                    logger.debug(
                        "ONVIFParser: Extracted %d '%s' elements", len(texts), name
                    )

        except (ValueError, TypeError, AttributeError) as e:
            logger.warning("ONVIFParser: Failed to extract elements: %s", e)

        return envelope, http_headers

    def get_extracted_texts(self, name: str, count: int) -> list[str | None]:
        """Get extracted element texts by name.

        Args:
            name (str): Name of the extracted elements (key from `extract_xpaths` dict)
            count (int): Number of elements to return

        Returns:
            List of element text values, padded with None if fewer elements were found.
                Example: If 3 elements found but `count=5`, returns [text1, text2, text3, None, None]
        """
        texts = self._extracted_elements.get(name, [])[:count]

        # Pad with None if not enough elements
        while len(texts) < count:
            texts.append(None)

        return texts


class XMLCapturePlugin(Plugin):
    """Zeep plugin to capture and inspect SOAP XML requests and responses.

    This plugin intercepts SOAP communication between the ONVIF client and device,
    capturing raw XML for debugging, logging, and analysis purposes. It's invaluable
    for understanding SOAP message structure and troubleshooting device communication.

    Attributes:
        pretty_print (bool): Whether to format XML with indentation
        last_sent_xml (str | None): Most recent request XML
        last_received_xml (str | None): Most recent response XML
        last_operation (str | None): Most recent operation name
        history (list[dict[str, Any]]): All captured requests/responses with metadata

    !!! tip "Version History"
        - Available since [`>=v0.0.6`](/onvif-python/releases/#v0.0.6).
        - Moved to `plugins` since [`>=v0.4.0`](/onvif-python/releases/#v0.4.0).

    !!! abstract "The plugin automatically captures"
        - Outgoing SOAP requests (`egress`)
        - Incoming SOAP responses (`ingress`)
        - HTTP headers for both directions
        - Operation names for context
        - Complete history of all transactions

    !!! danger "Use Cases"
        1. **Debugging**: See exact SOAP messages being sent/received
        2. **Learning**: Understand ONVIF protocol structure
        3. **Testing**: Verify request format and response structure
        4. **Documentation**: Extract examples for documentation
        5. **Troubleshooting**: Diagnose device compatibility issues
        6. **Development**: Test SOAP message modifications

    !!! warning "Performance Considerations"
        - Pretty printing adds minimal overhead (~5-10ms per request)
        - History storage grows with each request (clear periodically)
        - Large responses may consume significant memory
        - Consider disabling in production for high-volume applications

    ??? example "History Item Structure"
        ```python
        {
            'type': 'request' or 'response',
            'operation': 'GetDeviceInformation',
            'xml': '<soap:Envelope>...</soap:Envelope>',
            'http_headers': {'Content-Type': 'text/xml', ...}
        }
        ```

    ??? note "Notes"
        - Plugin is automatically created when `capture_xml=True`
        - Captured XML includes SOAP envelope, headers, and body
        - HTTP headers are captured as dictionaries
        - History preserves chronological order
        - Pretty printing uses lxml for reliable formatting
        - All captured data is stored in memory

    ??? note "See Also"
        - `zeep.Plugin`: Base class for zeep plugins
        - [`ONVIFClient`](../core/onvif_client.md): Client that uses this plugin
        - `lxml.etree`: XML processing library
    """

    def __init__(self, pretty_print=True):
        """Initialize XML capture plugin.

        Args:
            pretty_print (bool): If True, format XML with indentation
        """
        self.pretty_print = pretty_print
        self.last_sent_xml = None
        self.last_received_xml = None
        self.last_operation = None
        self.history = []  # Store all requests/responses
        logger.debug("XMLCapturePlugin initialized (pretty_print=%s)", pretty_print)

    def _format_xml(self, element) -> str:
        """Format XML element with proper indentation using lxml.

        Args:
            element: lxml Element to format

        Returns:
            Pretty-printed XML string
        """
        try:
            # Convert element to string first
            xml_bytes = etree.tostring(element, encoding="utf-8")

            # Re-parse with parser that removes blank text
            # This is safe as we control the input (it's from zeep)
            parser = etree.XMLParser(
                remove_blank_text=True, resolve_entities=False, no_network=True
            )
            reparsed = etree.fromstring(xml_bytes, parser)

            # Now pretty print the cleaned tree
            xml_string = etree.tostring(
                reparsed, pretty_print=True, encoding="unicode", xml_declaration=False
            )
            logger.debug("XML formatted successfully")
            return xml_string.strip()
        except Exception as e:  # pylint: disable=broad-except
            # Fallback to non-pretty printed version
            logger.warning("XML formatting failed, using fallback: %s", e)
            return etree.tostring(element, pretty_print=False, encoding="unicode")

    def egress(
        self,
        envelope: etree._Element,
        http_headers: dict[str, str],
        operation: Any,
        binding_options: dict[str, object],
    ):
        """Capture a SOAP request before it is sent to the device.

        This Zeep ``egress`` hook serializes the outgoing SOAP envelope and stores
        it in `last_sent_xml`. The request is also appended to `history` together
        with the operation name and HTTP headers.

        The original envelope and HTTP headers are returned unchanged, so this
        hook only observes the outgoing request and does not modify it.

        Args:
            envelope: SOAP request envelope that is about to be sent.
            http_headers: HTTP request headers that will be sent with the request.
            operation: Zeep operation being invoked.
            binding_options: Zeep binding options for the current request.

        Returns:
            A tuple containing the unchanged ``envelope`` and ``http_headers``.
        """
        logger.debug(
            "Capturing outgoing SOAP request for operation: %s", operation.name
        )

        # Serialize XML with proper pretty printing
        if self.pretty_print:
            self.last_sent_xml = self._format_xml(envelope)
        else:
            self.last_sent_xml = etree.tostring(
                envelope, pretty_print=False, encoding="unicode"
            )

        self.last_operation = operation.name

        # Store in history
        self.history.append(
            {
                "type": "request",
                "operation": operation.name,
                "xml": self.last_sent_xml,
                "http_headers": dict(http_headers) if http_headers else {},
            }
        )

        logger.debug(
            "Captured SOAP request for %s (%d chars)",
            operation.name,
            len(self.last_sent_xml),
        )
        return envelope, http_headers

    def ingress(
        self, envelope: etree._Element, http_headers: dict[str, str], operation: Any
    ):
        """Capture a SOAP response after it is received from the device.

        This Zeep ``ingress`` hook serializes the incoming SOAP envelope and stores
        it in `last_received_xml`. The response is also appended to `history`
        together with the operation name and HTTP headers.

        The original envelope and HTTP headers are returned unchanged, so this
        hook only observes the incoming response and does not modify it.

        Args:
            envelope: Raw SOAP response envelope received from the device.
            http_headers: HTTP response headers returned by the device.
            operation: Zeep operation associated with the response.

        Returns:
            A tuple containing the unchanged ``envelope`` and ``http_headers``.
        """
        logger.debug(
            "Capturing incoming SOAP response for operation: %s", operation.name
        )

        # Serialize XML with proper pretty printing
        if self.pretty_print:
            self.last_received_xml = self._format_xml(envelope)
        else:
            self.last_received_xml = etree.tostring(
                envelope, pretty_print=False, encoding="unicode"
            )

        # Store in history
        self.history.append(
            {
                "type": "response",
                "operation": operation.name,
                "xml": self.last_received_xml,
                "http_headers": dict(http_headers) if http_headers else {},
            }
        )

        logger.debug(
            "Captured SOAP response for %s (%d chars)",
            operation.name,
            len(self.last_received_xml),
        )
        return envelope, http_headers

    def get_last_request(self) -> str | None:
        """Get the last captured request XML.

        Returns:
            Last captured request XML
        """
        return self.last_sent_xml

    def get_last_response(self) -> str | None:
        """Get the last captured response XML.

        Returns:
            Last captured response XML
        """
        return self.last_received_xml

    def get_history(self) -> list:
        """Get all captured requests and responses.

        Returns:
            List of all captured requests and responses.
        """
        return self.history

    def clear_history(self) -> None:
        """Clear the capture history."""
        history_count = len(self.history)
        self.history = []
        self.last_sent_xml = None
        self.last_received_xml = None
        self.last_operation = None
        logger.debug("Cleared XML capture history (%d items)", history_count)

    def save_to_file(self, request_file=None, response_file=None) -> None:
        """Save captured XML to files.

        Args:
            request_file (str): Path to save request XML
            response_file (str): Path to save response XML
        """
        if request_file and self.last_sent_xml:
            try:
                with open(request_file, "w", encoding="utf-8") as f:
                    f.write(self.last_sent_xml)
                logger.info("Saved SOAP request XML to: %s", request_file)
            except OSError as e:
                logger.error("Failed to save request XML to %s: %s", request_file, e)

        if response_file and self.last_received_xml:
            try:
                with open(response_file, "w", encoding="utf-8") as f:
                    f.write(self.last_received_xml)
                logger.info("Saved SOAP response XML to: %s", response_file)
            except OSError as e:
                logger.error("Failed to save response XML to %s: %s", response_file, e)


class ReferenceParametersPlugin(Plugin):
    """Zeep plugin for injecting WS-Addressing reference parameters.

    The plugin adds WS-Addressing reference parameters to the SOAP ``Header``
    of outgoing requests. It is primarily useful for ONVIF services whose
    endpoint references contain ``ReferenceParameters`` that must be included
    in subsequent SOAP requests.

    Reference parameters are deep-copied before insertion so the original
    XML elements can be reused safely across requests.

    Attributes:
        reference_parameters: XML elements to inject into outgoing SOAP
            headers.

    !!! tip "Version History"
        - Available since [`>=v0.3.1`](/onvif-python/releases/#v0.3.1).

    !!! note

        The plugin supports both SOAP 1.1 and SOAP 1.2 envelope namespaces.
    """

    SOAP_NAMESPACES = (
        "http://schemas.xmlsoap.org/soap/envelope/",
        "http://www.w3.org/2003/05/soap-envelope",
    )

    def __init__(self, reference_parameters: list[etree._Element] | None = None):
        self.reference_parameters = reference_parameters or []

    def egress(
        self,
        envelope: etree._Element,
        http_headers: dict[str, str],
        operation: Any,
        binding_options: dict[str, object],
    ):
        """Inject WS-Addressing reference parameters into a SOAP request.

        This Zeep ``egress`` hook adds the configured reference parameters to the
        SOAP ``Header`` before the request is sent to the device.

        If the SOAP envelope does not contain a ``Header`` element, one is created.
        Reference parameters are deep-copied before being inserted so the original
        XML elements remain unchanged and can safely be reused.

        Args:
            envelope: SOAP request envelope that is about to be sent.
            http_headers: HTTP request headers that will be sent with the request.
            operation: Zeep operation being invoked.
            binding_options: Zeep binding options for the current request.

        Returns:
            A tuple containing the modified ``envelope`` and the unchanged ``http_headers``.

        Raises:
            RuntimeError: If the SOAP envelope uses an unsupported SOAP namespace.
        """
        soap_namespace = etree.QName(envelope).namespace

        if soap_namespace not in self.SOAP_NAMESPACES:
            raise RuntimeError(f"Unsupported SOAP envelope namespace: {soap_namespace}")

        header = envelope.find(f"{{{soap_namespace}}}Header")

        if header is None:
            header = etree.Element(f"{{{soap_namespace}}}Header")
            envelope.insert(0, header)

        for parameter in self.reference_parameters:
            header.append(deepcopy(parameter))

        return envelope, http_headers
