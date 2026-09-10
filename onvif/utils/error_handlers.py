"""ONVIFErrorHandler: Error handling utilities for ONVIF operations."""

import logging
from typing import Any

from zeep.exceptions import Fault

from onvif.utils.exceptions import ONVIFOperationException

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
    def is_action_not_supported(exception) -> bool:
        """Check whether an exception is caused by an ActionNotSupported SOAP fault."""
        try:
            # Handle ONVIFOperationException
            if isinstance(exception, ONVIFOperationException):
                original = exception.original_exception
            else:
                original = exception

            if not isinstance(original, Fault):
                return False

            subcodes = getattr(original, "subcodes", None)
            if not subcodes:
                return False

            for subcode in subcodes:
                localname = getattr(subcode, "localname", None)

                if localname == "ActionNotSupported":
                    logger.debug("Detected ActionNotSupported fault")
                    return True

                if "ActionNotSupported" in str(subcode):
                    logger.debug("Detected ActionNotSupported fault in subcode")
                    return True

        except OSError as error:
            logger.debug("Error checking ActionNotSupported: %s", error)

        return False

    @staticmethod
    def safe_call(
        func, default=None, ignore_unsupported=True, log_error=True
    ) -> Any | None:
        """Safely call an ONVIF operation with graceful error handling."""
        try:
            result = func()
            logger.debug("Safe call succeeded")
            return result
        except ONVIFOperationException as e:
            # Check if it's ActionNotSupported error
            if ignore_unsupported and ONVIFErrorHandler.is_action_not_supported(e):
                if log_error:
                    logger.warning("Operation not supported: %s", e.operation)
                return default
            # Re-raise other errors
            if log_error:
                logger.error("ONVIF operation failed in safe_call: %s", e.operation)
            raise
        except Exception as e:  # pylint: disable=broad-except
            # Wrap unexpected exceptions
            if log_error:
                logger.error("Unexpected error in safe_call: %s", e)
            raise

    @staticmethod
    def ignore_unsupported(func) -> Any | None:
        """Decorator to ignore ActionNotSupported SOAP faults.

        Returns None for unsupported operations, raises other exceptions.
        """

        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logger.debug("Decorated function %s succeeded", func.__name__)
                return result
            except ONVIFOperationException as e:
                if ONVIFErrorHandler.is_action_not_supported(e):
                    logger.warning(
                        "Operation not supported in %s: %s", func.__name__, e.operation
                    )
                    return None
                logger.error(
                    "ONVIF operation failed in %s: %s", func.__name__, e.operation
                )
                raise

        return wrapper
