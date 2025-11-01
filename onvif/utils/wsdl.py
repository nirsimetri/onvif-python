# onvif/utils/wsdl.py

import os
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ONVIFWSDL:
    """WSDL file manager for ONVIF services.

    This class manages WSDL (Web Services Description Language) file paths, bindings,
    and namespaces for all ONVIF services. It provides a centralized mapping between
    service names and their corresponding WSDL definitions.

    The class supports both built-in WSDLs (bundled with the package) and custom
    WSDL directories for users who want to use their own WSDL files.

    Features:
        - Centralized WSDL definition mapping for all ONVIF services
        - Support for multiple ONVIF versions (ver10, ver20)
        - Custom WSDL directory support (global and per-call)
        - Automatic path resolution for built-in and custom WSDLs
        - Service discovery with namespace and binding information
        - File existence validation

    WSDL Structure:
        Built-in WSDLs are organized in ONVIF standard directory structure:
        - onvif/wsdl/ver10/device/wsdl/devicemgmt.wsdl
        - onvif/wsdl/ver20/media/wsdl/media.wsdl
        - onvif/wsdl/ver20/ptz/wsdl/ptz.wsdl
        etc.

        Custom WSDLs can use flat structure:
        - /custom/path/devicemgmt.wsdl
        - /custom/path/media.wsdl
        - /custom/path/ptz.wsdl

    Service Definition Format:
        Each service has a definition containing:
        - path: Full path to WSDL file
        - binding: SOAP binding name (e.g., "DeviceBinding")
        - namespace: XML namespace URI (e.g., "http://www.onvif.org/ver10/device/wsdl")

    Custom WSDL Directory Priority:
        1. Per-call custom_wsdl_dir parameter (highest priority)
        2. Global _custom_wsdl_dir setting
        3. Built-in BASE_DIR (default)

    Notes:
        - All methods are class methods - no need to instantiate
        - WSDL files are lazy-loaded and validated on access
        - Custom WSDL directories use flat file structure
        - Built-in WSDLs follow ONVIF standard directory structure
        - File existence is checked when getting definitions
        - Thread-safe for read operations

    See Also:
        - ONVIFOperator: Uses WSDL definitions to create SOAP clients
        - ONVIFClient: High-level client that uses this class internally
    """

    # Default base directory for WSDL files (Built-in)
    # Included in the package
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wsdl")

    # Global custom WSDL directory - can be set once for all services
    _custom_wsdl_dir = None

    @classmethod
    def set_custom_wsdl_dir(cls, custom_dir):
        """Set global custom WSDL directory for all services.

        Args:
            custom_dir (str): Path to directory containing custom WSDL files

        Example:
            >>> ONVIFWSDL.set_custom_wsdl_dir("/home/user/my_wsdls")
            >>> # All subsequent get_definition calls will use this directory
        """
        logger.info(f"Setting custom WSDL directory: {custom_dir}")
        cls._custom_wsdl_dir = custom_dir

    @classmethod
    def get_custom_wsdl_dir(cls):
        """Get current global custom WSDL directory.

        Returns:
            str or None: Current custom WSDL directory, or None if using built-in

        Example:
            >>> ONVIFWSDL.set_custom_wsdl_dir("/custom/path")
            >>> print(ONVIFWSDL.get_custom_wsdl_dir())  # /custom/path
        """
        return cls._custom_wsdl_dir

    @classmethod
    def clear_custom_wsdl_dir(cls):
        """Clear custom WSDL directory, revert to built-in WSDLs.

        Example:
            >>> ONVIFWSDL.set_custom_wsdl_dir("/custom/path")
            >>> ONVIFWSDL.clear_custom_wsdl_dir()
            >>> # Now using built-in WSDLs again
        """
        logger.info("Clearing custom WSDL directory, reverting to built-in WSDLs")
        cls._custom_wsdl_dir = None

    @classmethod
    def _get_base_dir(cls, custom_wsdl_dir=None):
        """Get the base WSDL directory, using custom directory if provided.

        This method implements the priority chain for WSDL directory resolution.

        Args:
            custom_wsdl_dir (str, optional): Per-call custom directory

        Returns:
            str: Resolved WSDL base directory path

        Priority:
            1. custom_wsdl_dir parameter (highest)
            2. cls._custom_wsdl_dir global setting
            3. cls.BASE_DIR built-in default (lowest)
        """
        # Priority: parameter > global setting > default
        if custom_wsdl_dir:
            return custom_wsdl_dir
        elif cls._custom_wsdl_dir:
            return cls._custom_wsdl_dir
        else:
            return cls.BASE_DIR

    @classmethod
    def _get_wsdl_map(cls, custom_wsdl_dir=None):
        """Get WSDL map with proper base directory.

        Generates a complete mapping of all ONVIF services to their WSDL definitions.
        The structure differs based on whether custom WSDLs are used.

        Args:
            custom_wsdl_dir (str, optional): Custom WSDL directory path

        Returns:
            dict: Complete WSDL mapping for all services

        WSDL Map Structure:
            {
                "{service_name}": {
                    "{version}": {
                        "path": "/full/path/to/service.wsdl",
                        "binding": "ServiceBinding",
                        "namespace": "http://www.onvif.org/ver10/service/wsdl"
                    }
                }
            }

        Path Resolution:
            - Built-in: Uses ONVIF standard directory structure
              Example: ver10/device/wsdl/devicemgmt.wsdl
            - Custom: Uses flat structure with direct filename
              Example: devicemgmt.wsdl
        """
        base_dir = cls._get_base_dir(custom_wsdl_dir)

        # Determine if we should use flat structure
        # Use flat structure if custom_wsdl_dir is explicitly provided OR if global custom dir is set
        use_flat = custom_wsdl_dir is not None or cls._custom_wsdl_dir is not None

        # Default structure for WSDL files
        # If custom_wsdl_dir is provided, use flat structure (direct filename)
        # Otherwise, use the standard ONVIF directory structure
        return {
            "devicemgmt": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "devicemgmt.wsdl"
                            if use_flat
                            else "ver10/device/wsdl/devicemgmt.wsdl"
                        ),
                    ),
                    "binding": "DeviceBinding",
                    "namespace": "http://www.onvif.org/ver10/device/wsdl",
                }
            },
            "events": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "event-vs.wsdl"
                            if use_flat
                            else "ver10/events/wsdl/event-vs.wsdl"
                        ),
                    ),
                    "binding": "EventBinding",
                    "namespace": "http://www.onvif.org/ver10/events/wsdl",
                }
            },
            "pullpoint": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "event-vs.wsdl"
                            if use_flat
                            else "ver10/events/wsdl/event-vs.wsdl"
                        ),
                    ),
                    "binding": "PullPointSubscriptionBinding",
                    "namespace": "http://www.onvif.org/ver10/events/wsdl",
                }
            },
            "notification": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "event-vs.wsdl"
                            if use_flat
                            else "ver10/events/wsdl/event-vs.wsdl"
                        ),
                    ),
                    "binding": "NotificationProducerBinding",
                    "namespace": "http://www.onvif.org/ver10/events/wsdl",
                }
            },
            "subscription": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "event-vs.wsdl"
                            if use_flat
                            else "ver10/events/wsdl/event-vs.wsdl"
                        ),
                    ),
                    "binding": "SubscriptionManagerBinding",
                    "namespace": "http://www.onvif.org/ver10/events/wsdl",
                }
            },
            "pausable_subscription": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "event-vs.wsdl"
                            if use_flat
                            else "ver10/events/wsdl/event-vs.wsdl"
                        ),
                    ),
                    "binding": "PausableSubscriptionManagerBinding",
                    "namespace": "http://www.onvif.org/ver10/events/wsdl",
                }
            },
            "accesscontrol": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "accesscontrol.wsdl"
                            if use_flat
                            else "ver10/pacs/accesscontrol.wsdl"
                        ),
                    ),
                    "binding": "PACSBinding",
                    "namespace": "http://www.onvif.org/ver10/accesscontrol/wsdl",
                }
            },
            "accessrules": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "accessrules.wsdl"
                            if use_flat
                            else "ver10/accessrules/wsdl/accessrules.wsdl"
                        ),
                    ),
                    "binding": "AccessRulesBinding",
                    "namespace": "http://www.onvif.org/ver10/accessrules/wsdl",
                }
            },
            "actionengine": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "actionengine.wsdl"
                            if use_flat
                            else "ver10/actionengine.wsdl"
                        ),
                    ),
                    "binding": "ActionEngineBinding",
                    "namespace": "http://www.onvif.org/ver10/actionengine/wsdl",
                }
            },
            "advancedsecurity": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "advancedsecurity.wsdl"
                            if use_flat
                            else "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                        ),
                    ),
                    "binding": "AdvancedSecurityServiceBinding",
                    "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
                }
            },
            "jwt": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "advancedsecurity.wsdl"
                            if use_flat
                            else "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                        ),
                    ),
                    "binding": "JWTBinding",
                    "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
                }
            },
            "keystore": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "advancedsecurity.wsdl"
                            if use_flat
                            else "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                        ),
                    ),
                    "binding": "KeystoreBinding",
                    "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
                }
            },
            "tlsserver": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "advancedsecurity.wsdl"
                            if use_flat
                            else "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                        ),
                    ),
                    "binding": "TLSServerBinding",
                    "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
                }
            },
            "dot1x": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "advancedsecurity.wsdl"
                            if use_flat
                            else "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                        ),
                    ),
                    "binding": "Dot1XBinding",
                    "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
                }
            },
            "authorizationserver": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "advancedsecurity.wsdl"
                            if use_flat
                            else "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                        ),
                    ),
                    "binding": "AuthorizationServerBinding",
                    "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
                }
            },
            "mediasigning": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "advancedsecurity.wsdl"
                            if use_flat
                            else "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                        ),
                    ),
                    "binding": "MediaSigningBinding",
                    "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
                }
            },
            "analytics": {
                "ver20": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "analytics.wsdl"
                            if use_flat
                            else "ver20/analytics/wsdl/analytics.wsdl"
                        ),
                    ),
                    "binding": "AnalyticsEngineBinding",
                    "namespace": "http://www.onvif.org/ver20/analytics/wsdl",
                }
            },
            "ruleengine": {
                "ver20": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "ruleengine.wsdl"
                            if use_flat
                            else "ver20/analytics/wsdl/analytics.wsdl"
                        ),
                    ),
                    "binding": "RuleEngineBinding",
                    "namespace": "http://www.onvif.org/ver20/analytics/wsdl",
                }
            },
            "analyticsdevice": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "analyticsdevice.wsdl"
                            if use_flat
                            else "ver10/analyticsdevice.wsdl"
                        ),
                    ),
                    "binding": "AnalyticsDeviceBinding",
                    "namespace": "http://www.onvif.org/ver10/analyticsdevice/wsdl",
                }
            },
            "appmgmt": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "appmgmt.wsdl"
                            if use_flat
                            else "ver10/appmgmt/wsdl/appmgmt.wsdl"
                        ),
                    ),
                    "binding": "AppManagementBinding",
                    "namespace": "http://www.onvif.org/ver10/appmgmt/wsdl",
                }
            },
            "authenticationbehavior": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "authenticationbehavior.wsdl"
                            if use_flat
                            else "ver10/authenticationbehavior/wsdl/authenticationbehavior.wsdl"
                        ),
                    ),
                    "binding": "AuthenticationBehaviorBinding",
                    "namespace": "http://www.onvif.org/ver10/authenticationbehavior/wsdl",
                }
            },
            "credential": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "credential.wsdl"
                            if use_flat
                            else "ver10/credential/wsdl/credential.wsdl"
                        ),
                    ),
                    "binding": "CredentialBinding",
                    "namespace": "http://www.onvif.org/ver10/credential/wsdl",
                }
            },
            "deviceio": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        "deviceio.wsdl" if use_flat else "ver10/deviceio.wsdl",
                    ),
                    "binding": "DeviceIOBinding",
                    "namespace": "http://www.onvif.org/ver10/deviceIO/wsdl",
                }
            },
            "display": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        "display.wsdl" if use_flat else "ver10/display.wsdl",
                    ),
                    "binding": "DisplayBinding",
                    "namespace": "http://www.onvif.org/ver10/display/wsdl",
                }
            },
            "doorcontrol": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "doorcontrol.wsdl"
                            if use_flat
                            else "ver10/pacs/doorcontrol.wsdl"
                        ),
                    ),
                    "binding": "DoorControlBinding",
                    "namespace": "http://www.onvif.org/ver10/doorcontrol/wsdl",
                }
            },
            "imaging": {
                "ver20": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "imaging.wsdl"
                            if use_flat
                            else "ver20/imaging/wsdl/imaging.wsdl"
                        ),
                    ),
                    "binding": "ImagingBinding",
                    "namespace": "http://www.onvif.org/ver20/imaging/wsdl",
                }
            },
            "media": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        ("media.wsdl" if use_flat else "ver10/media/wsdl/media.wsdl"),
                    ),
                    "binding": "MediaBinding",
                    "namespace": "http://www.onvif.org/ver10/media/wsdl",
                },
            },
            "media2": {
                "ver20": {
                    "path": os.path.join(
                        base_dir,
                        ("media2.wsdl" if use_flat else "ver20/media/wsdl/media.wsdl"),
                    ),
                    "binding": "Media2Binding",
                    "namespace": "http://www.onvif.org/ver20/media/wsdl",
                },
            },
            "provisioning": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "provisioning.wsdl"
                            if use_flat
                            else "ver10/provisioning/wsdl/provisioning.wsdl"
                        ),
                    ),
                    "binding": "ProvisioningBinding",
                    "namespace": "http://www.onvif.org/ver10/provisioning/wsdl",
                },
            },
            "ptz": {
                "ver20": {
                    "path": os.path.join(
                        base_dir,
                        "ptz.wsdl" if use_flat else "ver20/ptz/wsdl/ptz.wsdl",
                    ),
                    "binding": "PTZBinding",
                    "namespace": "http://www.onvif.org/ver20/ptz/wsdl",
                },
            },
            "receiver": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        "receiver.wsdl" if use_flat else "ver10/receiver.wsdl",
                    ),
                    "binding": "ReceiverBinding",
                    "namespace": "http://www.onvif.org/ver10/receiver/wsdl",
                },
            },
            "recording": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        "recording.wsdl" if use_flat else "ver10/recording.wsdl",
                    ),
                    "binding": "RecordingBinding",
                    "namespace": "http://www.onvif.org/ver10/recording/wsdl",
                },
            },
            "replay": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        "replay.wsdl" if use_flat else "ver10/replay.wsdl",
                    ),
                    "binding": "ReplayBinding",
                    "namespace": "http://www.onvif.org/ver10/replay/wsdl",
                },
            },
            "schedule": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "schedule.wsdl"
                            if use_flat
                            else "ver10/schedule/wsdl/schedule.wsdl"
                        ),
                    ),
                    "binding": "ScheduleBinding",
                    "namespace": "http://www.onvif.org/ver10/schedule/wsdl",
                },
            },
            "search": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        "search.wsdl" if use_flat else "ver10/search.wsdl",
                    ),
                    "binding": "SearchBinding",
                    "namespace": "http://www.onvif.org/ver10/search/wsdl",
                },
            },
            "thermal": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "thermal.wsdl"
                            if use_flat
                            else "ver10/thermal/wsdl/thermal.wsdl"
                        ),
                    ),
                    "binding": "ThermalBinding",
                    "namespace": "http://www.onvif.org/ver10/thermal/wsdl",
                },
            },
            "uplink": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "uplink.wsdl"
                            if use_flat
                            else "ver10/uplink/wsdl/uplink.wsdl"
                        ),
                    ),
                    "binding": "UplinkBinding",
                    "namespace": "http://www.onvif.org/ver10/uplink/wsdl",
                },
            },
        }

    WSDL_MAP = None  # Will be initialized when first accessed

    @classmethod
    def _ensure_wsdl_map_initialized(cls):
        """Ensure WSDL_MAP is initialized with default values.

        Lazy initialization of the default WSDL map. This is called automatically
        before accessing WSDL_MAP to ensure it's not None.
        """
        if cls.WSDL_MAP is None:
            cls.WSDL_MAP = cls._get_wsdl_map()

    @classmethod
    def get_definition(
        cls, service: str, version: str = "ver10", custom_wsdl_dir=None
    ) -> dict:
        """Get WSDL definition for a specific ONVIF service.

        Returns complete WSDL definition including file path, SOAP binding name,
        and XML namespace for the requested service and version.

        Args:
            service (str): Service name (e.g., "devicemgmt", "media", "ptz")
            version (str, optional): ONVIF version (default: "ver10")
                Common versions: "ver10", "ver20"
            custom_wsdl_dir (str, optional): Custom WSDL directory path
                Overrides global custom directory if provided

        Returns:
            dict: Service definition containing:
                - path (str): Full path to WSDL file
                - binding (str): SOAP binding name
                - namespace (str): XML namespace URI

        Notes:
            - Most services use ver10, some newer ones use ver20
            - Media has both ver10 (media) and ver20 (media2)
            - Custom WSDLs must match the service name exactly
            - File existence is validated before returning definition
        """
        logger.debug(f"Getting WSDL definition for service: {service} ({version})")

        # Use custom WSDL map if custom directory is provided
        if custom_wsdl_dir:
            logger.debug(f"Using custom WSDL directory: {custom_wsdl_dir}")
            wsdl_map = cls._get_wsdl_map(custom_wsdl_dir)
        else:
            # Ensure default WSDL_MAP is initialized
            cls._ensure_wsdl_map_initialized()
            wsdl_map = cls.WSDL_MAP

        # Safety check for None wsdl_map
        if wsdl_map is None:
            logger.error("Failed to initialize WSDL map")
            raise RuntimeError("Failed to initialize WSDL map")

        if service not in wsdl_map:
            logger.error(f"Unknown service: {service}")
            raise ValueError(f"Unknown service: {service}")
        if version not in wsdl_map[service]:
            logger.error(f"Version {version} not available for {service}")
            raise ValueError(f"Version {version} not available for {service}")

        definition = wsdl_map[service][version]
        if not os.path.exists(definition["path"]):
            logger.error(f"WSDL file not found: {definition['path']}")
            raise FileNotFoundError(f"WSDL file not found: {definition['path']}")

        logger.debug(f"WSDL definition resolved: {definition['path']}")
        return definition
