# onvif/utils/exceptions.py

from zeep.exceptions import Fault
import requests


class ONVIFOperationException(Exception):
    """Enhanced exception wrapper for ONVIF operation failures.

    This exception provides detailed error information including operation name,
    error category, SOAP fault details, and the original exception. It categorizes
    errors into three types: SOAP, Protocol, and Application errors.

    Attributes:
        operation (str): Name of the ONVIF operation that failed
        original_exception (Exception): The underlying exception that was raised

    Error Categories:
        1. **SOAP Error**: Device returned a SOAP fault (e.g., ActionNotSupported)
           - Includes fault code, subcode, message, and detail
           - Supports both SOAP 1.1 and 1.2 formats
           - Extracts readable information from XML fault details

        2. **Protocol Error**: Network/HTTP transport failed
           - Connection errors, timeouts, SSL errors
           - HTTP status errors (404, 401, 500, etc.)
           - DNS resolution failures

        3. **Application Error**: Generic/unexpected errors
           - Python exceptions, type errors, etc.
           - Fallback category for uncategorized errors

    Common SOAP Fault Subcodes:
        - ActionNotSupported: Operation not implemented by device
        - NotAuthorized: Authentication failed or insufficient permissions
        - InvalidArgVal: Invalid parameter value
        - OperationProhibited: Operation not allowed in current state
        - Sender: Client-side error in request
        - Receiver: Server-side error in device

    Example Error Messages:
        >>> # SOAP Error - ActionNotSupported
        >>> # ONVIF operation 'GetImagingSettings' failed: SOAP Error: code=Receiver, subcode=ActionNotSupported, msg=Optional Action Not Implemented
        >>>
        >>> # Protocol Error - Connection Timeout
        >>> # ONVIF operation 'GetCapabilities' failed: Protocol Error: HTTPConnectionPool(host='192.168.1.100', port=80): Read timed out.
        >>>
        >>> # SOAP Error - Invalid Argument
        >>> # ONVIF operation 'SetVideoEncoderConfiguration' failed: SOAP Error: code=Sender, subcode=InvalidArgVal, msg=Invalid resolution, detail=Width=1920, Height=1080
        >>>
        >>> # Application Error - Missing Argument
        >>> # ONVIF operation 'UpgradeSystemFirmware' failed: Application Error: TypeError - Device.UpgradeSystemFirmware() missing 1 required positional argument: 'Firmware'

    Notes:
        - Always wraps the original exception for full error context
        - Preserves stack trace through exception chaining
        - Extracts maximum information from SOAP fault details
        - Handles both lxml.etree.QName objects and strings in subcodes
        - Safe handling of missing or malformed fault information
        - Compatible with Python exception handling best practices

    See Also:
        - ONVIFErrorHandler: Utilities for handling specific error types
        - zeep.exceptions.Fault: Base SOAP fault exception
        - requests.exceptions.RequestException: Base HTTP error
    """

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
            if subcodes is not None:
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
                except Exception:
                    subcodes = str(subcodes)

            # Build comprehensive error message
            parts = []
            if code:
                parts.append(f"code={code}")
            if subcodes:
                parts.append(f"subcode={subcodes}")
            if message and message.strip():  # Only add if message has content
                parts.append(f"msg={message}")
            if detail is not None:
                # Parse XML detail element to extract readable content
                try:
                    if hasattr(detail, "text") and detail.text:
                        detail_text = detail.text.strip()
                    elif hasattr(detail, "__iter__"):
                        # Try to extract text from child elements
                        detail_parts = []
                        for child in detail:
                            if hasattr(child, "text") and child.text:
                                detail_parts.append(
                                    f"{child.tag.split('}')[-1]}={child.text}"
                                )
                            elif hasattr(child, "tag"):
                                detail_parts.append(child.tag.split("}")[-1])
                        detail_text = (
                            ", ".join(detail_parts) if detail_parts else str(detail)
                        )
                    else:
                        detail_text = str(detail)
                    parts.append(f"detail={detail_text}")
                except Exception:
                    # Fallback to string representation
                    parts.append(f"detail={str(detail)}")

            msg = f"{category}: {', '.join(parts)}"
        elif isinstance(original_exception, requests.exceptions.RequestException):
            # Transport/Protocol error
            category = "Protocol Error"
            msg = f"{category}: {str(original_exception)}"
        else:
            # Application or generic error
            category = "Application Error"

            # For better error messages, include exception type
            exception_type = type(original_exception).__name__
            exception_msg = str(original_exception)

            # For some exceptions like KeyError, TypeError, add more context
            if isinstance(original_exception, KeyError):
                msg = f"{category}: KeyError - Missing key {exception_msg}"
            elif isinstance(original_exception, TypeError):
                msg = f"{category}: TypeError - {exception_msg}"
            elif isinstance(original_exception, ValueError):
                msg = f"{category}: ValueError - {exception_msg}"
            elif isinstance(original_exception, AttributeError):
                msg = f"{category}: AttributeError - {exception_msg}"
            else:
                # Generic format with exception type
                msg = f"{category}: {exception_type} - {exception_msg}"

        super().__init__(f"ONVIF operation '{operation}' failed: {msg}")
