"""ONVIF XMLCapturePlugin: Zeep plugin to capture and inspect SOAP XML requests and responses for ONVIF operations."""

import logging

from lxml import etree
from zeep import Plugin

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


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
