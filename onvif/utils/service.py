# onvif/utils/service.py

from .exceptions import ONVIFOperationException


class ONVIFService:
    """
    All service classes (Device, Media, PTZ, etc.) inherit from this base class
    to ensure consistent error handling and API experience across ONVIF services.
    """

    def __getattribute__(self, name):
        """Intercept all method calls and wrap with error handling for ONVIF methods"""
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
