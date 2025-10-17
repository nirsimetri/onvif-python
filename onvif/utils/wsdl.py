# onvif/utils/wsdl.py

import os


class ONVIFWSDL:
    # Default base directory for WSDL files (Built-in)
    # Included in the package
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wsdl")

    # Global custom WSDL directory - can be set once for all services
    _custom_wsdl_dir = None

    @classmethod
    def set_custom_wsdl_dir(cls, custom_dir):
        """Set global custom WSDL directory for all services."""
        cls._custom_wsdl_dir = custom_dir

    @classmethod
    def get_custom_wsdl_dir(cls):
        """Get current global custom WSDL directory."""
        return cls._custom_wsdl_dir

    @classmethod
    def clear_custom_wsdl_dir(cls):
        """Clear custom WSDL directory, revert to built-in."""
        cls._custom_wsdl_dir = None

    @classmethod
    def _get_base_dir(cls, custom_wsdl_dir=None):
        """Get the base WSDL directory, using custom directory if provided."""
        # Priority: parameter > global setting > default
        if custom_wsdl_dir:
            return custom_wsdl_dir
        elif cls._custom_wsdl_dir:
            return cls._custom_wsdl_dir
        else:
            return cls.BASE_DIR

    @classmethod
    def _get_wsdl_map(cls, custom_wsdl_dir=None):
        """Get WSDL map with proper base directory."""
        base_dir = cls._get_base_dir(custom_wsdl_dir)

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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
                            else "ver10/events/wsdl/event-vs.wsdl"
                        ),
                    ),
                    "binding": "SubscriptionManagerBinding",
                    "namespace": "http://www.onvif.org/ver10/events/wsdl",
                }
            },
            "accesscontrol": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "accesscontrol.wsdl"
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                        "deviceio.wsdl" if custom_wsdl_dir else "ver10/deviceio.wsdl",
                    ),
                    "binding": "DeviceIOBinding",
                    "namespace": "http://www.onvif.org/ver10/deviceIO/wsdl",
                }
            },
            "display": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        "display.wsdl" if custom_wsdl_dir else "ver10/display.wsdl",
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
                        (
                            "media.wsdl"
                            if custom_wsdl_dir
                            else "ver10/media/wsdl/media.wsdl"
                        ),
                    ),
                    "binding": "MediaBinding",
                    "namespace": "http://www.onvif.org/ver10/media/wsdl",
                },
            },
            "media2": {
                "ver20": {
                    "path": os.path.join(
                        base_dir,
                        (
                            "media2.wsdl"
                            if custom_wsdl_dir
                            else "ver20/media/wsdl/media.wsdl"
                        ),
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
                            if custom_wsdl_dir
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
                        "ptz.wsdl" if custom_wsdl_dir else "ver20/ptz/wsdl/ptz.wsdl",
                    ),
                    "binding": "PTZBinding",
                    "namespace": "http://www.onvif.org/ver20/ptz/wsdl",
                },
            },
            "receiver": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        "receiver.wsdl" if custom_wsdl_dir else "ver10/receiver.wsdl",
                    ),
                    "binding": "ReceiverBinding",
                    "namespace": "http://www.onvif.org/ver10/receiver/wsdl",
                },
            },
            "recording": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        "recording.wsdl" if custom_wsdl_dir else "ver10/recording.wsdl",
                    ),
                    "binding": "RecordingBinding",
                    "namespace": "http://www.onvif.org/ver10/recording/wsdl",
                },
            },
            "replay": {
                "ver10": {
                    "path": os.path.join(
                        base_dir,
                        "replay.wsdl" if custom_wsdl_dir else "ver10/replay.wsdl",
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
                            if custom_wsdl_dir
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
                        "search.wsdl" if custom_wsdl_dir else "ver10/search.wsdl",
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
                            if custom_wsdl_dir
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
                            if custom_wsdl_dir
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
        """Ensure WSDL_MAP is initialized with default values."""
        if cls.WSDL_MAP is None:
            cls.WSDL_MAP = cls._get_wsdl_map()

    @classmethod
    def get_definition(
        cls, service: str, version: str = "ver10", custom_wsdl_dir=None
    ) -> dict:
        """
        Return WSDL definition including path, binding and namespace.

        Args:
            service (str): The service name.
            version (str): The service version. Defaults to "ver10".
            custom_wsdl_dir (str, optional): Custom WSDL directory path. If provided,
                returns definition using custom directory instead of default.

        Returns:
            dict: The service definition containing path, binding, and namespace.

        Raises:
            ValueError: If the service or version is not found.
            FileNotFoundError: If the WSDL file does not exist.
        """
        # Use custom WSDL map if custom directory is provided
        if custom_wsdl_dir:
            wsdl_map = cls._get_wsdl_map(custom_wsdl_dir)
        else:
            # Ensure default WSDL_MAP is initialized
            cls._ensure_wsdl_map_initialized()
            wsdl_map = cls.WSDL_MAP

        # Safety check for None wsdl_map
        if wsdl_map is None:
            raise RuntimeError("Failed to initialize WSDL map")

        if service not in wsdl_map:
            raise ValueError(f"Unknown service: {service}")
        if version not in wsdl_map[service]:
            raise ValueError(f"Version {version} not available for {service}")

        definition = wsdl_map[service][version]
        if not os.path.exists(definition["path"]):
            raise FileNotFoundError(f"WSDL file not found: {definition['path']}")

        return definition
