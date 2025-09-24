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
            code = getattr(original_exception, "faultcode", None)
            detail = getattr(original_exception, "detail", None)
            msg = f"{category}: code={code}, msg={str(original_exception)}, detail={detail}"
        elif isinstance(original_exception, requests.exceptions.RequestException):
            # Transport/Protocol error
            category = "Protocol Error"
            msg = f"{category}: {str(original_exception)}"
        else:
            # Application or generic error
            category = "Application Error"
            msg = f"{category}: {str(original_exception)}"

        super().__init__(f"ONVIF operation '{operation}' failed: {msg}")
