# onvif/utils/service.py

from .exceptions import ONVIFOperationException


class ONVIFService:
    """Base class for all ONVIF service implementations.

    This abstract base class provides automatic error handling and consistent API
    behavior for all ONVIF services (Device, Media, PTZ, Events, Analytics, etc.).

    All service classes inherit from ONVIFService to ensure:
        - Consistent exception handling across all ONVIF operations
        - Automatic wrapping of errors into ONVIFOperationException
        - Uniform error reporting with operation names
        - Transparent method interception without explicit wrappers

    Implementation Details:
        - Uses __getattribute__ magic method to intercept all method calls
        - Automatically wraps ONVIF operations (methods starting with uppercase)
        - Preserves non-ONVIF methods, private methods, and attributes
        - Converts all exceptions to ONVIFOperationException for consistency
        - Re-raises existing ONVIFOperationException without double-wrapping

    Method Detection Logic:
        The class identifies ONVIF operations by checking if the method name:
        1. Is callable (not a property or attribute)
        2. Starts with uppercase letter (ONVIF naming convention)
        3. Is not a private method (doesn't start with underscore)
        4. Is not an internal attribute (like 'operator')

    ONVIF operations that will be wrapped:
        ✓ GetDeviceInformation()
        ✓ GetProfiles()
        ✓ ContinuousMove()
        ✓ CreatePullPointSubscription()
        ✓ GetImagingSettings()

    Methods that will NOT be wrapped:
        ✗ _internal_method()  (starts with underscore)
        ✗ helper_function()   (starts with lowercase)
        ✗ operator            (internal attribute)
        ✗ non_callable_attr   (not a method)

    Benefits:
        1. **DRY Principle**: No need to repeat error handling in every method
        2. **Consistency**: All ONVIF operations behave the same way
        3. **Maintainability**: Error handling logic in one place
        4. **Debuggability**: Always know which operation failed
        5. **Transparency**: No boilerplate code in service implementations

    Notes:
        - This is an abstract base class - don't instantiate directly
        - Subclasses must implement their own __init__ and ONVIF methods
        - The __getattribute__ interception has minimal performance overhead
        - Error wrapping preserves full stack trace for debugging
        - Compatible with all Python magic methods and properties

    See Also:
        - ONVIFOperationException: Exception class for wrapped errors
        - ONVIFOperator: Low-level SOAP operation handler
        - Device, Media, PTZ, etc.: Concrete service implementations
    """

    def __getattribute__(self, name):
        """Intercept all method calls and wrap ONVIF operations with error handling.

        This magic method is called for every attribute access on the service object.
        It intercepts ONVIF operation calls and wraps them with consistent error handling.

        Args:
            name (str): Name of the attribute or method being accessed

        Returns:
            The attribute value, or a wrapped method if it's an ONVIF operation

        Raises:
            ONVIFOperationException: If the ONVIF operation fails

        Method Interception Logic:
            1. Get the attribute using object.__getattribute__
            2. Skip if not callable, private, or internal attribute
            3. Check if method name starts with uppercase (ONVIF convention)
            4. If yes, return wrapped version that catches and converts exceptions
            5. If no, return the original method as-is
        """
        attr = object.__getattribute__(self, name)

        # Skip non-callable attributes, private methods, and internal attributes
        if not callable(attr) or name.startswith("_") or name in ["operator"]:
            return attr

        # Check if this looks like an ONVIF method (starts with uppercase)
        if not name[0].isupper():
            return attr

        # Wrap ONVIF methods with error handling
        def wrapped_method(*args, **kwargs):
            try:
                return attr(*args, **kwargs)
            except ONVIFOperationException:
                # Re-raise ONVIF exceptions as-is
                raise
            except Exception as e:
                # Convert any other exception (including TypeError) to ONVIFOperationException
                raise ONVIFOperationException(name, e)

        return wrapped_method
