# onvif/utils/xml_capture.py

from zeep import Plugin
from lxml import etree
from xml.dom import minidom


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
        Format XML element with proper indentation using minidom.

        Args:
            element: lxml Element to format

        Returns:
            str: Pretty-printed XML string
        """
        try:
            # Convert lxml element to string
            xml_string = etree.tostring(element, encoding="unicode")
            # Parse with minidom and pretty print
            dom = minidom.parseString(xml_string)
            # Use toprettyxml with proper indentation
            pretty_xml = dom.toprettyxml(indent="  ", encoding=None)
            # Remove extra blank lines and XML declaration
            lines = [line for line in pretty_xml.split("\n") if line.strip()]
            # Remove XML declaration line if present
            if lines and lines[0].startswith("<?xml"):
                lines = lines[1:]
            return "\n".join(lines)
        except Exception:
            # Fallback to lxml if minidom fails
            return etree.tostring(element, pretty_print=True, encoding="unicode")

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
