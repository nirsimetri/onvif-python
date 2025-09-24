# onvif/utils/wsdl.py

import os


class ONVIFWSDL:
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wsdl")

    WSDL_MAP = {
        "devicemgmt": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/device/wsdl/devicemgmt.wsdl"),
                "binding": "DeviceBinding",
                "namespace": "http://www.onvif.org/ver10/device/wsdl",
            }
        },
        "events": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/events/wsdl/event-vs.wsdl"),
                "binding": "EventBinding",
                "namespace": "http://www.onvif.org/ver10/events/wsdl",
            }
        },
        "pullpoint": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/events/wsdl/event-vs.wsdl"),
                "binding": "PullPointSubscriptionBinding",
                "namespace": "http://www.onvif.org/ver10/events/wsdl",
            }
        },
        "notification": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/events/wsdl/event-vs.wsdl"),
                "binding": "NotificationProducerBinding",
                "namespace": "http://www.onvif.org/ver10/events/wsdl",
            }
        },
        "subscription": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/events/wsdl/event-vs.wsdl"),
                "binding": "SubscriptionManagerBinding",
                "namespace": "http://www.onvif.org/ver10/events/wsdl",
            }
        },
        "accesscontrol": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/pacs/accesscontrol.wsdl"),
                "binding": "PACSBinding",
                "namespace": "http://www.onvif.org/ver10/accesscontrol/wsdl",
            }
        },
        "accessrules": {
            "ver10": {
                "path": os.path.join(
                    BASE_DIR, "ver10/accessrules/wsdl/accessrules.wsdl"
                ),
                "binding": "AccessRulesBinding",
                "namespace": "http://www.onvif.org/ver10/accessrules/wsdl",
            }
        },
        "actionengine": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/actionengine.wsdl"),
                "binding": "ActionEngineBinding",
                "namespace": "http://www.onvif.org/ver10/actionengine/wsdl",
            }
        },
        "advancedsecurity": {
            "ver10": {
                "path": os.path.join(
                    BASE_DIR, "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                ),
                "binding": "AdvancedSecurityServiceBinding",
                "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
            }
        },
        "jwt": {
            "ver10": {
                "path": os.path.join(
                    BASE_DIR, "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                ),
                "binding": "JWTBinding",
                "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
            }
        },
        "keystore": {
            "ver10": {
                "path": os.path.join(
                    BASE_DIR, "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                ),
                "binding": "KeystoreBinding",
                "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
            }
        },
        "tlsserver": {
            "ver10": {
                "path": os.path.join(
                    BASE_DIR, "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                ),
                "binding": "TLSServerBinding",
                "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
            }
        },
        "dot1x": {
            "ver10": {
                "path": os.path.join(
                    BASE_DIR, "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                ),
                "binding": "Dot1XBinding",
                "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
            }
        },
        "authorizationserver": {
            "ver10": {
                "path": os.path.join(
                    BASE_DIR, "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                ),
                "binding": "AuthorizationServerBinding",
                "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
            }
        },
        "mediasigning": {
            "ver10": {
                "path": os.path.join(
                    BASE_DIR, "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl"
                ),
                "binding": "MediaSigningBinding",
                "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
            }
        },
        "analytics": {
            "ver20": {
                "path": os.path.join(BASE_DIR, "ver20/analytics/wsdl/analytics.wsdl"),
                "binding": "AnalyticsEngineBinding",
                "namespace": "http://www.onvif.org/ver20/analytics/wsdl",
            }
        },
        "ruleengine": {
            "ver20": {
                "path": os.path.join(BASE_DIR, "ver20/analytics/wsdl/analytics.wsdl"),
                "binding": "RuleEngineBinding",
                "namespace": "http://www.onvif.org/ver20/analytics/wsdl",
            }
        },
        "analyticsdevice": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/analyticsdevice.wsdl"),
                "binding": "AnalyticsDeviceBinding",
                "namespace": "http://www.onvif.org/ver10/analyticsdevice/wsdl",
            }
        },
        "appmgmt": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/appmgmt/wsdl/appmgmt.wsdl"),
                "binding": "AppManagementBinding",
                "namespace": "http://www.onvif.org/ver10/appmgmt/wsdl",
            }
        },
        "authenticationbehavior": {
            "ver10": {
                "path": os.path.join(
                    BASE_DIR,
                    "ver10/authenticationbehavior/wsdl/authenticationbehavior.wsdl",
                ),
                "binding": "AuthenticationBehaviorBinding",
                "namespace": "http://www.onvif.org/ver10/authenticationbehavior/wsdl",
            }
        },
        "credential": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/credential/wsdl/credential.wsdl"),
                "binding": "CredentialBinding",
                "namespace": "http://www.onvif.org/ver10/credential/wsdl",
            }
        },
        "deviceio": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/deviceio.wsdl"),
                "binding": "DeviceIOBinding",
                "namespace": "http://www.onvif.org/ver10/deviceIO/wsdl",
            }
        },
        "display": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/display.wsdl"),
                "binding": "DisplayBinding",
                "namespace": "http://www.onvif.org/ver10/display/wsdl",
            }
        },
        "doorcontrol": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/pacs/doorcontrol.wsdl"),
                "binding": "DoorControlBinding",
                "namespace": "http://www.onvif.org/ver10/doorcontrol/wsdl",
            }
        },
        "imaging": {
            "ver20": {
                "path": os.path.join(BASE_DIR, "ver20/imaging/wsdl/imaging.wsdl"),
                "binding": "ImagingBinding",
                "namespace": "http://www.onvif.org/ver20/imaging/wsdl",
            }
        },
        "media": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/media/wsdl/media.wsdl"),
                "binding": "MediaBinding",
                "namespace": "http://www.onvif.org/ver10/media/wsdl",
            },
        },
        "media2": {
            "ver20": {
                "path": os.path.join(BASE_DIR, "ver20/media/wsdl/media.wsdl"),
                "binding": "Media2Binding",
                "namespace": "http://www.onvif.org/ver20/media/wsdl",
            },
        },
        "provisioning": {
            "ver10": {
                "path": os.path.join(
                    BASE_DIR, "ver10/provisioning/wsdl/provisioning.wsdl"
                ),
                "binding": "ProvisioningBinding",
                "namespace": "http://www.onvif.org/ver10/provisioning/wsdl",
            },
        },
        "ptz": {
            "ver20": {
                "path": os.path.join(BASE_DIR, "ver20/ptz/wsdl/ptz.wsdl"),
                "binding": "PTZBinding",
                "namespace": "http://www.onvif.org/ver20/ptz/wsdl",
            },
        },
        "receiver": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/receiver.wsdl"),
                "binding": "ReceiverBinding",
                "namespace": "http://www.onvif.org/ver10/receiver/wsdl",
            },
        },
        "recording": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/recording.wsdl"),
                "binding": "RecordingBinding",
                "namespace": "http://www.onvif.org/ver10/recording/wsdl",
            },
        },
        "replay": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/replay.wsdl"),
                "binding": "ReplayBinding",
                "namespace": "http://www.onvif.org/ver10/replay/wsdl",
            },
        },
        "schedule": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/schedule/wsdl/schedule.wsdl"),
                "binding": "ScheduleBinding",
                "namespace": "http://www.onvif.org/ver10/schedule/wsdl",
            },
        },
        "search": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/search.wsdl"),
                "binding": "SearchBinding",
                "namespace": "http://www.onvif.org/ver10/search/wsdl",
            },
        },
        "thermal": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/thermal/wsdl/thermal.wsdl"),
                "binding": "ThermalBinding",
                "namespace": "http://www.onvif.org/ver10/thermal/wsdl",
            },
        },
        "uplink": {
            "ver10": {
                "path": os.path.join(BASE_DIR, "ver10/uplink/wsdl/uplink.wsdl"),
                "binding": "UplinkBinding",
                "namespace": "http://www.onvif.org/ver10/uplink/wsdl",
            },
        },
    }

    @classmethod
    def get_definition(cls, service: str, version: str = "ver10") -> dict:
        """Return WSDL definition including path, binding and namespace."""
        if service not in cls.WSDL_MAP:
            raise ValueError(f"Unknown service: {service}")
        if version not in cls.WSDL_MAP[service]:
            raise ValueError(f"Version {version} not available for {service}")

        definition = cls.WSDL_MAP[service][version]
        if not os.path.exists(definition["path"]):
            raise FileNotFoundError(f"WSDL file not found: {definition['path']}")

        return definition
