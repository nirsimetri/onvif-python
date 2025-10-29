# onvif/utils/error_handlers.py

import logging
from zeep.exceptions import Fault
from .exceptions import ONVIFOperationException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ONVIFErrorHandler:
    """Error handling utilities for ONVIF operations.

    This class provides static methods to gracefully handle ONVIF SOAP errors,
    particularly the common "ActionNotSupported" fault that occurs when devices
    don't implement certain optional ONVIF operations.

    ONVIF devices may not support all operations defined in the specification.
    When an unsupported operation is called, the device returns a SOAP fault with
    the "ActionNotSupported" subcode. This class helps detect and handle such cases.

    Key Features:
        - Detect ActionNotSupported SOAP faults
        - Provide safe operation calls with default fallbacks
        - Decorator pattern for ignoring unsupported operations
        - Wrapper for graceful degradation in multi-device environments

    Common Use Cases:
        1. **Feature Detection**: Check if device supports an operation
        2. **Graceful Degradation**: Continue execution when operation fails
        3. **Multi-Device Support**: Handle devices with varying capabilities
        4. **Safe Exploration**: Test operations without crashing

    Notes:
        - All methods are static - no need to instantiate the class
        - Works with both ONVIFOperationException and raw zeep.Fault
        - Preserves stack traces for non-ActionNotSupported errors
        - Minimal performance overhead for supported operations
        - Thread-safe (no shared state)

    See Also:
        - ONVIFOperationException: Custom exception wrapper
        - zeep.exceptions.Fault: Base SOAP fault exception
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
                                logger.debug("Detected ActionNotSupported fault")
                                return True
                        elif "ActionNotSupported" in str(subcode):
                            logger.debug("Detected ActionNotSupported fault in subcode")
                            return True
        except Exception as e:
            logger.debug(f"Error checking ActionNotSupported: {e}")
            pass

        return False

    @staticmethod
    def safe_call(func, default=None, ignore_unsupported=True, log_error=True):
        """Safely call an ONVIF operation with graceful error handling."""
        try:
            result = func()
            logger.debug("Safe call succeeded")
            return result
        except ONVIFOperationException as e:
            # Check if it's ActionNotSupported error
            if ignore_unsupported and ONVIFErrorHandler.is_action_not_supported(e):
                if log_error:
                    logger.warning(f"Operation not supported: {e.operation}")
                return default
            # Re-raise other errors
            if log_error:
                logger.error(f"ONVIF operation failed in safe_call: {e.operation}")
            raise
        except Exception as e:
            # Wrap unexpected exceptions
            if log_error:
                logger.error(f"Unexpected error in safe_call: {e}")
            raise

    @staticmethod
    def ignore_unsupported(func):
        """
        Decorator to ignore ActionNotSupported SOAP faults.
        Returns None for unsupported operations, raises other exceptions.
        """

        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Decorated function {func.__name__} succeeded")
                return result
            except ONVIFOperationException as e:
                if ONVIFErrorHandler.is_action_not_supported(e):
                    logger.warning(
                        f"Operation not supported in {func.__name__}: {e.operation}"
                    )
                    return None
                logger.error(
                    f"ONVIF operation failed in {func.__name__}: {e.operation}"
                )
                raise

        return wrapper
