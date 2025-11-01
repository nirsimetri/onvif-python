# onvif/utils/service.py

import logging
from .exceptions import ONVIFOperationException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


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
            except ONVIFOperationException as oe:
                # Re-raise ONVIF exceptions as-is
                service_name = getattr(self.operator, "service_name", "Unknown")
                logger.error(f"{service_name}.{name}: {oe}")
                raise
            except Exception as e:
                # Convert any other exception (including TypeError) to ONVIFOperationException
                service_name = getattr(self.operator, "service_name", "Unknown")
                logger.error(f"{service_name}.{name}: {e}")
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

    def desc(self, method_name: str):
        """
        Get documentation and parameter information for a specific operation/method.

        Args:
            method_name (str): Name of the method to describe (e.g., 'GetDeviceInformation', 'SetHostname')

        Returns:
            dict: Dictionary containing documentation and parameter information with keys:
                - 'doc': Method documentation from WSDL
                - 'required': List of required parameter names
                - 'optional': List of optional parameter names
                - 'method_name': The method name
                - 'service_name': The service name

        Raises:
            ONVIFOperationException: If method doesn't exist or documentation cannot be retrieved

        Example:
            device = client.devicemgmt()

            # Get description for a method
            info = device.desc('GetDeviceInformation')
            print(info['doc'])
            print("Required params:", info['required'])
            print("Optional params:", info['optional'])

            # Check what methods are available first
            methods = device.operations()
            info = device.desc(methods[0])  # Describe first method
        """
        try:
            # Check if method exists
            if not hasattr(self, method_name):
                available_methods = self.operations()
                raise ValueError(
                    f"Method '{method_name}' not found in service. "
                    f"Available methods: {', '.join(available_methods[:5])}{'...' if len(available_methods) > 5 else ''}"
                )

            # Extract service name from binding for context
            service_name = (
                self.operator.service_name
                if hasattr(self.operator, "service_name")
                else "Unknown"
            )

            # Always try to extract method parameters
            required_args = []
            optional_args = []
            doc_text = None

            try:
                # Use object.__getattribute__ to bypass ONVIFService wrapper and get original method
                import inspect

                method = object.__getattribute__(self, method_name)
                sig = inspect.signature(method)
                for param in sig.parameters.values():
                    if param.name != "self":
                        if param.default is inspect.Parameter.empty:
                            required_args.append(param.name)
                        else:
                            optional_args.append(param.name)

                logger.debug(
                    f"Successfully extracted parameters for {service_name}.{method_name}"
                )
            except Exception as param_error:
                logger.warning(
                    f"Could not extract parameters for {method_name}: {param_error}"
                )

            # Try to get documentation (optional)
            try:
                from ..cli.utils import get_method_documentation

                doc_info = get_method_documentation(self, method_name)
                if doc_info and doc_info.get("doc"):
                    # Only use doc if it's not the default "No description available" message
                    doc_text = doc_info["doc"]
                    if (
                        doc_text
                        and "No description available" not in doc_text
                        and "No documentation available" not in doc_text
                    ):
                        # Keep the doc text as is
                        pass
                    else:
                        # Set to None if it's the default message
                        doc_text = None
            except Exception as e:
                logger.warning(
                    f"Could not retrieve documentation for {method_name}: {e}"
                )  # Documentation is optional

            return {
                "doc": doc_text,
                "required": required_args,
                "optional": optional_args,
                "method_name": method_name,
                "service_name": service_name,
            }

        except Exception as e:
            logger.error(f"Failed to get description for method {method_name}: {e}")
            raise ONVIFOperationException(f"desc({method_name})", e)

    def operations(self):
        """
        List all available operations for this service.

        Returns:
            List of operation names that can be used with type() method
        """
        try:
            # Get all methods from the service object itself (not operator.service)
            # This includes all ONVIF operations that are dynamically added
            operations = [
                method
                for method in dir(self)
                if not method.startswith("_")
                and method not in ["type", "desc", "operations"]
                and callable(getattr(self, method))
                and method[0].isupper()  # ONVIF methods start with uppercase
            ]
            # Extract service name from binding for logging context
            service_name = (
                self.operator.service_name
                if hasattr(self.operator, "service_name")
                else "Unknown"
            )
            logger.debug(
                f"Successfully listed operations for {service_name}: {len(operations)} operations found"
            )
            return sorted(operations)
        except Exception as e:
            logger.error(f"Failed to list operations: {e}")
            return []
