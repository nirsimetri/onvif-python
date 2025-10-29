# onvif/utils/service.py

import logging
from .exceptions import ONVIFOperationException

logger = logging.getLogger(__name__)


def _is_zeep_object(obj):
    """Check if an object is a Zeep-generated object.

    Zeep objects have the _xsd_type attribute which is the XSD type definition.
    """
    return hasattr(obj, "_xsd_type")


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

        # Wrap ONVIF methods with error handling and Zeep object conversion
        def wrapped_method(*args, **kwargs):
            try:
                # If called with 1 positional arg that is a Zeep object and no kwargs,
                # convert the object's fields to kwargs instead of passing it as positional arg
                if len(args) == 1 and not kwargs and _is_zeep_object(args[0]):
                    params_obj = args[0]
                    logger.debug(f"Converting Zeep object to kwargs for {name}")
                    # Extract fields from Zeep object using its XSD type elements
                    if hasattr(params_obj._xsd_type, "elements"):
                        kwargs = {}
                        for elem_name, elem_obj in params_obj._xsd_type.elements:
                            kwargs[elem_name] = getattr(params_obj, elem_name)
                        return attr(**kwargs)

                logger.debug(f"Calling wrapped ONVIF method: {name}")
                result = attr(*args, **kwargs)
                logger.debug(f"ONVIF method {name} completed successfully")
                return result
            except ONVIFOperationException:
                # Re-raise ONVIF exceptions as-is
                logger.error(f"ONVIF operation exception in {name}")
                raise
            except Exception as e:
                # Convert any other exception (including TypeError) to ONVIFOperationException
                logger.error(f"Exception in {name}: {e}")
                raise ONVIFOperationException(name, e)

        return wrapped_method

    def type(self, type_name: str):
        """
        Create and return an instance of the specified ONVIF type.

        Args:
            type_name (str): Name of the type to create (e.g., 'SetHostname', 'SetIPAddressFilter')

        Returns:
            Type instance that can be populated with data

        Raises:
            ONVIFOperationException: If type creation fails

        Example:
            device = client.devicemgmt()

            newuser = device.type('CreateUsers')
            newuser.User.append({"Username": 'new_user', "Password": 'new_password', "UserLevel": 'User'})
            device.CreateUsers(newuser)

            hostname = device.type('SetHostname')
            hostname.Name = 'NewHostname'
            device.SetHostname(hostname)

            time_params = device.type('SetSystemDateAndTime')
            time_params.DateTimeType = 'NTP'
            time_params.DaylightSavings = True
            time_params.TimeZone.TZ = 'UTC+02:00'
            now = datetime.now()
            time_params.UTCDateTime.Date.Year = now.year
            time_params.UTCDateTime.Date.Month = now.month
            time_params.UTCDateTime.Date.Day = now.day
            time_params.UTCDateTime.Time.Hour = now.hour
            time_params.UTCDateTime.Time.Minute = now.minute
            time_params.UTCDateTime.Time.Second = now.second
            device.SetSystemDateAndTime(time_params)
        """
        try:
            logger.debug(f"Creating ONVIF type: {type_name}")
            result = self.operator.create_type(type_name)
            logger.debug(f"Successfully created type: {type_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to create type {type_name}: {e}")
            raise ONVIFOperationException(f"type({type_name})", e)
