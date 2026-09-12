"""
Error handling utilities for ONVIF operations.

This module provides utilities to gracefully handle ONVIF SOAP errors,
particularly the common `ActionNotSupported` fault that occurs when devices
don't implement certain optional ONVIF operations.

ONVIF devices may not support all operations defined in the specification.
When an unsupported operation is called, the device returns a SOAP fault with
the `ActionNotSupported` subcode. These utilities help detect and handle such
cases.

!!! abstract "Features"
    - Detect `ActionNotSupported` SOAP faults
    - Provide safe operation calls with default fallbacks
    - Ignore unsupported operations using a decorator
    - Support graceful degradation in multi-device environments

!!! tip "Common Use Cases"
    1. **Feature Detection**: Check if a device supports an operation
    2. **Graceful Degradation**: Continue execution when an operation fails
    3. **Multi-Device Support**: Handle devices with varying capabilities
    4. **Safe Exploration**: Test operations without crashing

??? note "Notes"
    - Works with both `ONVIFOperationException` and raw `zeep.Fault`
    - Preserves stack traces for non-`ActionNotSupported` errors
    - Minimal performance overhead for supported operations
    - Thread-safe because no shared state is maintained

??? note "See Also"
    - [`ONVIFOperationException`](onvif_exception.md): Custom exception wrapper
    - `zeep.exceptions.Fault`: Base SOAP fault exception
"""

import logging
from typing import Any

from zeep.exceptions import Fault

from onvif.utils.exceptions import ONVIFOperationException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def is_action_not_supported(exception) -> bool:
    """
    Check whether an exception is caused by an `ActionNotSupported` SOAP fault.

    Args:
        exception: The exception to inspect. Can be an
            `ONVIFOperationException` or a raw `zeep.exceptions.Fault`.

    Returns:
        `True` if the exception contains an `ActionNotSupported` SOAP fault, `False` otherwise.

    Example:
        ```python
        from onvif import ONVIFClient, is_action_not_supported

        try:
            client = ONVIFClient("192.168.1.17", 80, "admin", "password")
            device = client.devicemgmt()
            system_uris = device.GetSystemUris()
        except ONVIFOperationException as e:
            if is_action_not_supported(e):
                # Fallback: Get basic device information
                device_info = device.GetDeviceInformation()
        ```
    """
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


def safe_call(
    func, default=None, handle_unsupported=True, log_error=True
) -> Any | None:
    """
    Safely call an ONVIF operation with graceful error handling.

    Args:
        func: The callable that performs the ONVIF operation.
        default: The value to return when the operation is unsupported and
            `handle_unsupported` is enabled. Defaults to `None`.
        handle_unsupported: Whether to catch `ActionNotSupported` faults and
            return `default` instead of raising the exception. Defaults to
            `True`.
        log_error: Whether to log errors encountered during the operation.
            Defaults to `True`.

    Returns:
        The result returned by `func`, or `default` when the operation is
            unsupported and `handle_unsupported` is enabled.

    Raises:
        ONVIFOperationException: If the operation fails for a reason other
            than `ActionNotSupported`, or if `handle_unsupported` is disabled.
        Exception: If `func` raises an unexpected exception.

    Example:
        ```python
        from onvif import ONVIFClient, safe_call

        client = ONVIFClient("192.168.1.17", 80, "admin", "password")
        device = client.devicemgmt()

        # Returns None if operation is not supported
        ip_filter = safe_call(device.GetIPAddressFilter)

        if ip_filter:
            print(f"IP Address Filter: {ip_filter}")
        else:
            print("GetIPAddressFilter not supported or returned None")

        services = safe_call(
            lambda: device.GetServices(IncludeCapability=False),
            handle_unsupported=False  # Raise exception if not supported
        )

        print(f"Found {len(services)} services")
        ```
    """
    try:
        result = func()
        logger.debug("Safe call succeeded")
        return result
    except ONVIFOperationException as e:
        # Check if it's ActionNotSupported error
        if handle_unsupported and is_action_not_supported(e):
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


def ignore_unsupported(func) -> Any | None:
    """Decorator to ignore `ActionNotSupported` SOAP faults.

    Args:
        func: The function to decorate. The function may accept positional
            and keyword arguments.

    Returns:
        A wrapped function that returns `None` when an `ActionNotSupported` fault occurs.

    Raises:
        ONVIFOperationException: If the decorated function fails for a reason
            other than `ActionNotSupported`.
        Exception: If the decorated function raises an unexpected exception.

    Example:
        ```python
        from onvif import ONVIFClient, ignore_unsupported

        client = ONVIFClient("192.168.1.17", 80, "admin", "password")
        device = client.devicemgmt()

        @ignore_unsupported
        def get_zero_configuration():
            return device.GetZeroConfiguration()

        @ignore_unsupported
        def get_ntp():
            return device.GetNTP()

        zero_conf = get_zero_configuration()
        if zero_conf:
            print(f"Zero Configuration: {zero_conf}")
        else:
            print("GetZeroConfiguration not supported")

        ntp = get_ntp()
        if ntp:
            print(f"NTP: {ntp}")
        else:
            print("GetNTP not supported")
        ```
    """

    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            logger.debug("Decorated function %s succeeded", func.__name__)
            return result
        except ONVIFOperationException as e:
            if is_action_not_supported(e):
                logger.warning(
                    "Operation not supported in %s: %s", func.__name__, e.operation
                )
                return None
            logger.error("ONVIF operation failed in %s: %s", func.__name__, e.operation)
            raise

    return wrapper
