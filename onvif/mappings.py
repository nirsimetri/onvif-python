"""Static mappings for ONVIF specifications and service metadata."""

from datetime import date
from typing import Final, TypedDict


class WSDLDefinition(TypedDict):
    """ONVIF WSDL definition."""

    filename: str
    path: str
    binding: str
    namespace: str


WSDLMap = dict[str, dict[str, WSDLDefinition]]

ONVIF_WSDL_MAP: Final[WSDLMap] = {
    "devicemgmt": {
        "ver10": {
            "filename": "devicemgmt.wsdl",
            "path": "ver10/device/wsdl/devicemgmt.wsdl",
            "binding": "DeviceBinding",
            "namespace": "http://www.onvif.org/ver10/device/wsdl",
        }
    },
    "events": {
        "ver10": {
            "filename": "event-vs.wsdl",
            "path": "ver10/events/wsdl/event-vs.wsdl",
            "binding": "EventBinding",
            "namespace": "http://www.onvif.org/ver10/events/wsdl",
        }
    },
    "pullpoint": {
        "ver10": {
            "filename": "event-vs.wsdl",
            "path": "ver10/events/wsdl/event-vs.wsdl",
            "binding": "PullPointSubscriptionBinding",
            "namespace": "http://www.onvif.org/ver10/events/wsdl",
        }
    },
    "notification": {
        "ver10": {
            "filename": "event-vs.wsdl",
            "path": "ver10/events/wsdl/event-vs.wsdl",
            "binding": "NotificationProducerBinding",
            "namespace": "http://www.onvif.org/ver10/events/wsdl",
        }
    },
    "subscription": {
        "ver10": {
            "filename": "event-vs.wsdl",
            "path": "ver10/events/wsdl/event-vs.wsdl",
            "binding": "SubscriptionManagerBinding",
            "namespace": "http://www.onvif.org/ver10/events/wsdl",
        }
    },
    "pausable_subscription": {
        "ver10": {
            "filename": "event-vs.wsdl",
            "path": "ver10/events/wsdl/event-vs.wsdl",
            "binding": "PausableSubscriptionManagerBinding",
            "namespace": "http://www.onvif.org/ver10/events/wsdl",
        }
    },
    "accesscontrol": {
        "ver10": {
            "filename": "accesscontrol.wsdl",
            "path": "ver10/pacs/accesscontrol.wsdl",
            "binding": "PACSBinding",
            "namespace": "http://www.onvif.org/ver10/accesscontrol/wsdl",
        }
    },
    "accessrules": {
        "ver10": {
            "filename": "accessrules.wsdl",
            "path": "ver10/accessrules/wsdl/accessrules.wsdl",
            "binding": "AccessRulesBinding",
            "namespace": "http://www.onvif.org/ver10/accessrules/wsdl",
        }
    },
    "actionengine": {
        "ver10": {
            "filename": "actionengine.wsdl",
            "path": "ver10/actionengine.wsdl",
            "binding": "ActionEngineBinding",
            "namespace": "http://www.onvif.org/ver10/actionengine/wsdl",
        }
    },
    "advancedsecurity": {
        "ver10": {
            "filename": "advancedsecurity.wsdl",
            "path": "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl",
            "binding": "AdvancedSecurityServiceBinding",
            "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
        }
    },
    "jwt": {
        "ver10": {
            "filename": "advancedsecurity.wsdl",
            "path": "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl",
            "binding": "JWTBinding",
            "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
        }
    },
    "keystore": {
        "ver10": {
            "filename": "advancedsecurity.wsdl",
            "path": "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl",
            "binding": "KeystoreBinding",
            "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
        }
    },
    "tlsserver": {
        "ver10": {
            "filename": "advancedsecurity.wsdl",
            "path": "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl",
            "binding": "TLSServerBinding",
            "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
        }
    },
    "dot1x": {
        "ver10": {
            "filename": "advancedsecurity.wsdl",
            "path": "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl",
            "binding": "Dot1XBinding",
            "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
        }
    },
    "authorizationserver": {
        "ver10": {
            "filename": "advancedsecurity.wsdl",
            "path": "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl",
            "binding": "AuthorizationServerBinding",
            "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
        }
    },
    "mediasigning": {
        "ver10": {
            "filename": "advancedsecurity.wsdl",
            "path": "ver10/advancedsecurity/wsdl/advancedsecurity.wsdl",
            "binding": "MediaSigningBinding",
            "namespace": "http://www.onvif.org/ver10/advancedsecurity/wsdl",
        }
    },
    "analytics": {
        "ver20": {
            "filename": "analytics.wsdl",
            "path": "ver20/analytics/wsdl/analytics.wsdl",
            "binding": "AnalyticsEngineBinding",
            "namespace": "http://www.onvif.org/ver20/analytics/wsdl",
        }
    },
    "ruleengine": {
        "ver20": {
            "filename": "analytics.wsdl",
            "path": "ver20/analytics/wsdl/analytics.wsdl",
            "binding": "RuleEngineBinding",
            "namespace": "http://www.onvif.org/ver20/analytics/wsdl",
        }
    },
    "analyticsdevice": {
        "ver10": {
            "filename": "analyticsdevice.wsdl",
            "path": "ver10/analyticsdevice.wsdl",
            "binding": "AnalyticsDeviceBinding",
            "namespace": "http://www.onvif.org/ver10/analyticsdevice/wsdl",
        }
    },
    "appmgmt": {
        "ver10": {
            "filename": "appmgmt.wsdl",
            "path": "ver10/appmgmt/wsdl/appmgmt.wsdl",
            "binding": "AppManagementBinding",
            "namespace": "http://www.onvif.org/ver10/appmgmt/wsdl",
        }
    },
    "authenticationbehavior": {
        "ver10": {
            "filename": "authenticationbehavior.wsdl",
            "path": "ver10/authenticationbehavior/wsdl/authenticationbehavior.wsdl",
            "binding": "AuthenticationBehaviorBinding",
            "namespace": "http://www.onvif.org/ver10/authenticationbehavior/wsdl",
        }
    },
    "credential": {
        "ver10": {
            "filename": "credential.wsdl",
            "path": "ver10/credential/wsdl/credential.wsdl",
            "binding": "CredentialBinding",
            "namespace": "http://www.onvif.org/ver10/credential/wsdl",
        }
    },
    "deviceio": {
        "ver10": {
            "filename": "deviceio.wsdl",
            "path": "ver10/deviceio.wsdl",
            "binding": "DeviceIOBinding",
            "namespace": "http://www.onvif.org/ver10/deviceIO/wsdl",
        }
    },
    "display": {
        "ver10": {
            "filename": "display.wsdl",
            "path": "ver10/display.wsdl",
            "binding": "DisplayBinding",
            "namespace": "http://www.onvif.org/ver10/display/wsdl",
        }
    },
    "doorcontrol": {
        "ver10": {
            "filename": "doorcontrol.wsdl",
            "path": "ver10/pacs/doorcontrol.wsdl",
            "binding": "DoorControlBinding",
            "namespace": "http://www.onvif.org/ver10/doorcontrol/wsdl",
        }
    },
    "imaging": {
        "ver20": {
            "filename": "imaging.wsdl",
            "path": "ver20/imaging/wsdl/imaging.wsdl",
            "binding": "ImagingBinding",
            "namespace": "http://www.onvif.org/ver20/imaging/wsdl",
        }
    },
    "media": {
        "ver10": {
            "filename": "media.wsdl",
            "path": "ver10/media/wsdl/media.wsdl",
            "binding": "MediaBinding",
            "namespace": "http://www.onvif.org/ver10/media/wsdl",
        },
    },
    "media2": {
        "ver20": {
            "filename": "media2.wsdl",
            "path": "ver20/media/wsdl/media.wsdl",
            "binding": "Media2Binding",
            "namespace": "http://www.onvif.org/ver20/media/wsdl",
        },
    },
    "provisioning": {
        "ver10": {
            "filename": "provisioning.wsdl",
            "path": "ver10/provisioning/wsdl/provisioning.wsdl",
            "binding": "ProvisioningBinding",
            "namespace": "http://www.onvif.org/ver10/provisioning/wsdl",
        },
    },
    "ptz": {
        "ver20": {
            "filename": "ptz.wsdl",
            "path": "ver20/ptz/wsdl/ptz.wsdl",
            "binding": "PTZBinding",
            "namespace": "http://www.onvif.org/ver20/ptz/wsdl",
        },
    },
    "receiver": {
        "ver10": {
            "filename": "receiver.wsdl",
            "path": "ver10/receiver.wsdl",
            "binding": "ReceiverBinding",
            "namespace": "http://www.onvif.org/ver10/receiver/wsdl",
        },
    },
    "recording": {
        "ver10": {
            "filename": "recording.wsdl",
            "path": "ver10/recording.wsdl",
            "binding": "RecordingBinding",
            "namespace": "http://www.onvif.org/ver10/recording/wsdl",
        },
    },
    "replay": {
        "ver10": {
            "filename": "replay.wsdl",
            "path": "ver10/replay.wsdl",
            "binding": "ReplayBinding",
            "namespace": "http://www.onvif.org/ver10/replay/wsdl",
        },
    },
    "schedule": {
        "ver10": {
            "filename": "schedule.wsdl",
            "path": "ver10/schedule/wsdl/schedule.wsdl",
            "binding": "ScheduleBinding",
            "namespace": "http://www.onvif.org/ver10/schedule/wsdl",
        },
    },
    "search": {
        "ver10": {
            "filename": "search.wsdl",
            "path": "ver10/search.wsdl",
            "binding": "SearchBinding",
            "namespace": "http://www.onvif.org/ver10/search/wsdl",
        },
    },
    "thermal": {
        "ver10": {
            "filename": "thermal.wsdl",
            "path": "ver10/thermal/wsdl/thermal.wsdl",
            "binding": "ThermalBinding",
            "namespace": "http://www.onvif.org/ver10/thermal/wsdl",
        },
    },
    "uplink": {
        "ver10": {
            "filename": "uplink.wsdl",
            "path": "ver10/uplink/wsdl/uplink.wsdl",
            "binding": "UplinkBinding",
            "namespace": "http://www.onvif.org/ver10/uplink/wsdl",
        },
    },
}

# ONVIF namespace to service name mapping (used globally)
# Format: namespace -> list of (service_name, binding_pattern)
# binding_pattern is used to identify specific binding in multi-binding services
ONVIF_NAMESPACE_MAP: Final[dict[str, tuple[tuple[str, str], ...]]] = {
    "http://www.onvif.org/ver10/device/wsdl": (("devicemgmt", "DeviceBinding"),),
    "http://www.onvif.org/ver10/events/wsdl": (
        ("events", "EventBinding"),
        ("pullpoint", "PullPointSubscriptionBinding"),
        ("notification", "NotificationProducerBinding"),
        ("subscription", "SubscriptionManagerBinding"),
        ("pausable_subscription", "PausableSubscriptionManagerBinding"),
    ),
    "http://www.onvif.org/ver20/imaging/wsdl": (("imaging", "ImagingBinding"),),
    "http://www.onvif.org/ver10/media/wsdl": (("media", "MediaBinding"),),
    "http://www.onvif.org/ver20/media/wsdl": (("media2", "Media2Binding"),),
    "http://www.onvif.org/ver20/ptz/wsdl": (("ptz", "PTZBinding"),),
    "http://www.onvif.org/ver10/deviceIO/wsdl": (("deviceio", "DeviceIOBinding"),),
    "http://www.onvif.org/ver10/display/wsdl": (("display", "DisplayBinding"),),
    "http://www.onvif.org/ver20/analytics/wsdl": (
        ("analytics", "AnalyticsEngineBinding"),
        ("ruleengine", "RuleEngineBinding"),
    ),
    "http://www.onvif.org/ver10/analyticsdevice/wsdl": (
        ("analyticsdevice", "AnalyticsDeviceBinding"),
    ),
    "http://www.onvif.org/ver10/accesscontrol/wsdl": (
        ("accesscontrol", "PACSBinding"),
    ),
    "http://www.onvif.org/ver10/doorcontrol/wsdl": (
        ("doorcontrol", "DoorControlBinding"),
    ),
    "http://www.onvif.org/ver10/accessrules/wsdl": (
        ("accessrules", "AccessRulesBinding"),
    ),
    "http://www.onvif.org/ver10/actionengine/wsdl": (
        ("actionengine", "ActionEngineBinding"),
    ),
    "http://www.onvif.org/ver10/provisioning/wsdl": (
        ("provisioning", "ProvisioningBinding"),
    ),
    "http://www.onvif.org/ver10/receiver/wsdl": (("receiver", "ReceiverBinding"),),
    "http://www.onvif.org/ver10/recording/wsdl": (("recording", "RecordingBinding"),),
    "http://www.onvif.org/ver10/replay/wsdl": (("replay", "ReplayBinding"),),
    "http://www.onvif.org/ver10/schedule/wsdl": (("schedule", "ScheduleBinding"),),
    "http://www.onvif.org/ver10/search/wsdl": (("search", "SearchBinding"),),
    "http://www.onvif.org/ver10/thermal/wsdl": (("thermal", "ThermalBinding"),),
    "http://www.onvif.org/ver10/uplink/wsdl": (("uplink", "UplinkBinding"),),
    "http://www.onvif.org/ver10/appmgmt/wsdl": (("appmgmt", "AppManagementBinding"),),
    "http://www.onvif.org/ver10/authenticationbehavior/wsdl": (
        ("authenticationbehavior", "AuthenticationBehaviorBinding"),
    ),
    "http://www.onvif.org/ver10/credential/wsdl": (
        ("credential", "CredentialBinding"),
    ),
    "http://www.onvif.org/ver10/advancedsecurity/wsdl": (
        ("advancedsecurity", "AdvancedSecurityServiceBinding"),
        ("jwt", "JWTBinding"),
        ("keystore", "KeystoreBinding"),
        ("tlsserver", "TLSServerBinding"),
        ("dot1x", "Dot1XBinding"),
        ("authorizationserver", "AuthorizationServerBinding"),
        ("mediasigning", "MediaSigningBinding"),
    ),
}

ONVIF_VERSION_MAP: Final[dict[tuple[int, int], date]] = {
    # 2008–2015 only
    (1, 0): date(2008, 11, 1),
    (1, 10): date(2009, 7, 1),
    (1, 20): date(2010, 6, 1),
    (2, 0): date(2010, 11, 1),
    (2, 10): date(2011, 6, 1),
    (2, 11): date(2012, 1, 1),
    (2, 20): date(2012, 9, 1),
    (2, 21): date(2012, 12, 1),
    (2, 30): date(2013, 5, 1),
    (2, 40): date(2013, 8, 1),
    (2, 41): date(2013, 12, 1),
    (2, 42): date(2014, 6, 1),
    (2, 50): date(2014, 12, 1),
    (2, 60): date(2015, 6, 1),
    (2, 61): date(2015, 12, 1),
    # Modern version (2016 +) will use the {Year}.{Month} format.
}
