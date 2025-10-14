# onvif/utils/exceptions.py

"""
(1) SOAP Errors
(2) Transport/Protocol Errors
(3) Application Errors
"""

from zeep.exceptions import Fault
import requests


class ONVIFOperationException(Exception):
    def __init__(self, operation, original_exception):
        self.operation = operation
        self.original_exception = original_exception

        if isinstance(original_exception, Fault):
            # SOAP-level error
            category = "SOAP Error"

            # Extract fault information (supports both SOAP 1.1 and 1.2)
            code = getattr(original_exception, "code", None) or getattr(
                original_exception, "faultcode", None
            )
            subcodes = getattr(original_exception, "subcodes", None)
            message = getattr(original_exception, "message", None) or str(
                original_exception
            )
            detail = getattr(original_exception, "detail", None)

            # Convert subcodes from QName objects to readable strings
            if subcodes:
                try:
                    # subcodes is a list of lxml.etree.QName objects
                    # QName objects have .localname (e.g., "ActionNotSupported")
                    # and .namespace (e.g., "http://www.onvif.org/ver10/error")
                    subcode_strings = []
                    for qname in subcodes:
                        if hasattr(qname, "localname"):
                            # Use only the local name without namespace
                            subcode_strings.append(qname.localname)
                        else:
                            # Fallback to string representation
                            subcode_strings.append(str(qname))
                    subcodes = ", ".join(subcode_strings)
                except:
                    subcodes = str(subcodes)

            # Build comprehensive error message
            parts = [f"code={code}"]
            if subcodes:
                parts.append(f"subcode={subcodes}")
            if message:
                parts.append(f"msg={message}")
            if detail:
                parts.append(f"detail={detail}")

            msg = f"{category}: {', '.join(parts)}"
        elif isinstance(original_exception, requests.exceptions.RequestException):
            # Transport/Protocol error
            category = "Protocol Error"
            msg = f"{category}: {str(original_exception)}"
        else:
            # Application or generic error
            category = "Application Error"
            msg = f"{category}: {str(original_exception)}"

        super().__init__(f"ONVIF operation '{operation}' failed: {msg}")
