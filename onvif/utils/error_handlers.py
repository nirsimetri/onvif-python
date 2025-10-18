# onvif/utils/error_handlers.py

from zeep.exceptions import Fault
from .exceptions import ONVIFOperationException


class ONVIFErrorHandler:
    """
    Error handling utilities for ONVIF operations.

    Provides static methods to handle ONVIF errors gracefully,
    especially ActionNotSupported SOAP faults.
    """

    @staticmethod
    def is_action_not_supported(exception):
        """Check if an ONVIFOperationException is caused by ActionNotSupported SOAP fault."""
        try:
            # Handle ONVIFOperationException
            if isinstance(exception, ONVIFOperationException):
                original = exception.original_exception
            else:
                original = exception

            # Check if it's a Fault with subcodes
            if isinstance(original, Fault):
                subcodes = getattr(original, "subcodes", None)
                if subcodes:
                    for subcode in subcodes:
                        if hasattr(subcode, "localname"):
                            if subcode.localname == "ActionNotSupported":
                                return True
                        elif "ActionNotSupported" in str(subcode):
                            return True
        except Exception:
            pass

        return False

    @staticmethod
    def safe_call(func, default=None, ignore_unsupported=True, log_error=True):
        """Safely call an ONVIF operation with graceful error handling."""
        try:
            return func()
        except ONVIFOperationException as e:
            # Check if it's ActionNotSupported error
            if ignore_unsupported and ONVIFErrorHandler.is_action_not_supported(e):
                # if log_error:
                # logging.warning(f"Operation not supported: {e.operation}")
                return default
            # Re-raise other errors
            raise
        except Exception:
            # Wrap unexpected exceptions
            # if log_error:
            # logging.error(f"Unexpected error in safe_call: {e}")
            raise

    @staticmethod
    def ignore_unsupported(func):
        """
        Decorator to ignore ActionNotSupported SOAP faults.
        Returns None for unsupported operations, raises other exceptions.
        """

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ONVIFOperationException as e:
                if ONVIFErrorHandler.is_action_not_supported(e):
                    # logging.warning(f"Operation not supported: {e.operation}")
                    return None
                raise

        return wrapper
