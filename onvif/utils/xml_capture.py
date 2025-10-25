# onvif/utils/xml_capture.py

from zeep import Plugin
from lxml import etree


class XMLCapturePlugin(Plugin):
    """
    Zeep plugin to capture SOAP XML requests and responses.

    Usage:
        client = ONVIFClient(host, port, user, pass, capture_xml=True)
        device = client.devicemgmt()
        result = device.GetServices()

        # Access captured XML
        print(client.xml_plugin.last_sent_xml)
        print(client.xml_plugin.last_received_xml)

        # Or get all history
        for item in client.xml_plugin.history:
            print(f"{item['operation']}: {item['type']}")
    """

    def __init__(self, pretty_print=True):
        """
        Initialize XML capture plugin.

        Args:
            pretty_print (bool): If True, format XML with indentation
        """
        self.pretty_print = pretty_print
        self.last_sent_xml = None
        self.last_received_xml = None
        self.last_operation = None
        self.history = []  # Store all requests/responses

    def _format_xml(self, element):
        """
        Format XML element with proper indentation using lxml.

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
            return xml_string.strip()
        except Exception:
            # Fallback to non-pretty printed version
            return etree.tostring(element, pretty_print=False, encoding="unicode")

    def egress(self, envelope, http_headers, operation, binding_options):
        """Called before sending the SOAP request"""
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

        return envelope, http_headers

    def ingress(self, envelope, http_headers, operation):
        """Called after receiving the SOAP response"""
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

        return envelope, http_headers

    def get_last_request(self):
        """Get the last captured request XML"""
        return self.last_sent_xml

    def get_last_response(self):
        """Get the last captured response XML"""
        return self.last_received_xml

    def get_history(self):
        """Get all captured requests and responses"""
        return self.history

    def clear_history(self):
        """Clear the capture history"""
        self.history = []
        self.last_sent_xml = None
        self.last_received_xml = None
        self.last_operation = None

    def save_to_file(self, request_file=None, response_file=None):
        """
        Save captured XML to files.

        Args:
            request_file (str): Path to save request XML
            response_file (str): Path to save response XML
        """
        if request_file and self.last_sent_xml:
            with open(request_file, "w", encoding="utf-8") as f:
                f.write(self.last_sent_xml)

        if response_file and self.last_received_xml:
            with open(response_file, "w", encoding="utf-8") as f:
                f.write(self.last_received_xml)
