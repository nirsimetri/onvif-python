"""Auxiliary custom Zeep plugins outside the core scope."""

from __future__ import annotations

import logging
from copy import deepcopy

from lxml import etree
from zeep import Plugin

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ONVIFParser(Plugin):
    """Lightweight Zeep plugin to extract XML elements from SOAP responses using XPath.

    This plugin extracts specific XML elements from raw SOAP responses before zeep
    parses them into Python objects. This is useful for extracting data that zeep
    doesn't parse correctly, such as simpleContent elements with attributes (e.g., Topic).

    Unlike XMLCapturePlugin which stores full XML history in memory, ONVIFParser only
    extracts and caches specified element texts from the last response.

    Usage Example 1 - Extract Topic from event notifications:
        >>> from onvif import ONVIFClient
        >>> from onvif.utils import ONVIFParser
        >>>
        >>> # Create parser to extract Topic elements
        >>> parser = ONVIFParser(extract_xpaths={
        ...     'topic': './/{http://docs.oasis-open.org/wsn/b-2}Topic'
        ... })
        >>>
        >>> # Pass parser to client as plugin
        >>> client = ONVIFClient(host, port, user, pass, plugins=[parser])
        >>>
        >>> # Make SOAP call
        >>> pullpoint = client.pullpoint(subscription)
        >>> msgs = pullpoint.PullMessages(Timeout="PT5S", MessageLimit=10)
        >>>
        >>> # Extract topic texts (cache auto-cleared on next SOAP call)
        >>> topics = parser.get_extracted_texts('topic', count=10)
        >>> for topic in topics:
        ...     print(f"Topic: {topic}")

    Usage Example 2 - Extract multiple elements:
        >>> parser = ONVIFParser(extract_xpaths={
        ...     'topic': './/{http://docs.oasis-open.org/wsn/b-2}Topic',
        ...     'custom': './/ns:CustomElement'
        ... })
        >>> client = ONVIFClient(host, port, user, pass, plugins=[parser])
        >>>
        >>> # After SOAP call
        >>> topics = parser.get_extracted_texts('topic', count=5)
        >>> customs = parser.get_extracted_texts('custom', count=5)

    Notes:
        - Uses ingress() hook to access raw XML before zeep parsing
        - Cache automatically cleared on each SOAP response
        - Thread-safe for single client usage
        - Works with any XPath expression
    """

    def __init__(self, extract_xpaths: dict[str, str]):
        """Initialize XML element parser.

        Args:
            extract_xpaths: Dictionary mapping names to XPath expressions.
                            XPath expressions will be used to find elements in SOAP response.
        Example:
        {
            'topic': './/{http://docs.oasis-open.org/wsn/b-2}Topic',
            'custom': './/ns:CustomElement'
        }
        """
        self.extract_xpaths = extract_xpaths
        self._extracted_elements: dict[str, list[str | None]] = {}

        logger.debug(
            "ONVIFParser initialized with XPaths: %s", list(extract_xpaths.keys())
        )

    def ingress(self, envelope, http_headers, _):
        """
        Zeep plugin hook - called when SOAP response is received.

        Extracts element texts from raw XML envelope using configured XPath expressions.
        The envelope at this stage is an lxml Element tree, allowing XPath queries.

        Cache is automatically cleared before extracting new elements
        to prevent memory accumulation.

        Args:
            envelope: lxml Element representing SOAP envelope
            http_headers: HTTP response headers
            operation: Zeep operation being executed

        Returns:
            Tuple of (envelope, http_headers) to pass to next plugin
        """
        # Auto-clear cache from previous response
        self._extracted_elements: dict[str, list[str | None]] = {}

        try:
            # Extract elements using XPath from raw XML envelope
            for name, xpath in self.extract_xpaths.items():
                elements = envelope.findall(xpath)

                # Extract text content from found elements
                texts = [elem.text for elem in elements if elem.text]

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
            name (str): Name of the extracted elements (key from extract_xpaths dict)
            count (int): Number of elements to return

        Returns:
            List of element text values, padded with None if fewer elements were found.
            Example: If 3 elements found but count=5, returns [text1, text2, text3, None, None]
        """
        texts = self._extracted_elements.get(name, [])[:count]

        # Pad with None if not enough elements
        while len(texts) < count:
            texts.append(None)

        return texts


SOAP_NAMESPACES = (
    "http://schemas.xmlsoap.org/soap/envelope/",
    "http://www.w3.org/2003/05/soap-envelope",
)


class ReferenceParametersPlugin(Plugin):
    """Inject WS-Addressing ReferenceParameters into SOAP headers."""

    def __init__(self, reference_parameters):
        self.reference_parameters = reference_parameters or []

    def egress(self, envelope, http_headers, operation, binding_options):
        soap_namespace = etree.QName(envelope).namespace

        if soap_namespace not in SOAP_NAMESPACES:
            raise RuntimeError(f"Unsupported SOAP envelope namespace: {soap_namespace}")

        header = envelope.find(f"{{{soap_namespace}}}Header")

        if header is None:
            header = etree.Element(f"{{{soap_namespace}}}Header")
            envelope.insert(0, header)

        for parameter in self.reference_parameters:
            header.append(deepcopy(parameter))

        return envelope, http_headers


class XMLCapturePlugin(Plugin):
    """Zeep plugin to capture and inspect SOAP XML requests and responses.

    This plugin intercepts SOAP communication between the ONVIF client and device,
    capturing raw XML for debugging, logging, and analysis purposes. It's invaluable
    for understanding SOAP message structure and troubleshooting device communication.

    The plugin automatically captures:
        - Outgoing SOAP requests (egress)
        - Incoming SOAP responses (ingress)
        - HTTP headers for both directions
        - Operation names for context
        - Complete history of all transactions

    Use Cases:
        1. **Debugging**: See exact SOAP messages being sent/received
        2. **Learning**: Understand ONVIF protocol structure
        3. **Testing**: Verify request format and response structure
        4. **Documentation**: Extract examples for documentation
        5. **Troubleshooting**: Diagnose device compatibility issues
        6. **Development**: Test SOAP message modifications

    Attributes:
        pretty_print (bool): Whether to format XML with indentation
        last_sent_xml (str): Most recent request XML
        last_received_xml (str): Most recent response XML
        last_operation (str): Most recent operation name
        history (list): All captured requests/responses with metadata

    History Item Structure:
        {
            'type': 'request' or 'response',
            'operation': 'GetDeviceInformation',
            'xml': '<soap:Envelope>...</soap:Envelope>',
            'http_headers': {'Content-Type': 'text/xml', ...}
        }

    Performance Considerations:
        - Pretty printing adds minimal overhead (~5-10ms per request)
        - History storage grows with each request (clear periodically)
        - Large responses may consume significant memory
        - Consider disabling in production for high-volume applications

    Notes:
        - Plugin is automatically created when capture_xml=True
        - Captured XML includes SOAP envelope, headers, and body
        - HTTP headers are captured as dictionaries
        - History preserves chronological order
        - Pretty printing uses lxml for reliable formatting
        - All captured data is stored in memory

    See Also:
        - zeep.Plugin: Base class for zeep plugins
        - ONVIFClient: Client that uses this plugin
        - lxml.etree: XML processing library
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
            str: Pretty-printed XML string
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

    def egress(self, envelope, http_headers, operation, binding_options):
        """Called before sending the SOAP request."""
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

    def ingress(self, envelope, http_headers, operation):
        """Called after receiving the SOAP response."""
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
        """Get the last captured request XML."""
        return self.last_sent_xml

    def get_last_response(self) -> str | None:
        """Get the last captured response XML."""
        return self.last_received_xml

    def get_history(self) -> list:
        """Get all captured requests and responses."""
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
