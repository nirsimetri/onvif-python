"""ONVIF services client."""

from onvif.services.accesscontrol import AccessControl
from onvif.services.accessrules import AccessRules
from onvif.services.actionengine import ActionEngine
from onvif.services.analytics.analytics import Analytics
from onvif.services.analytics.ruleengine import RuleEngine
from onvif.services.analyticsdevice import AnalyticsDevice
from onvif.services.appmgmt import AppManagement
from onvif.services.authenticationbehavior import AuthenticationBehavior
from onvif.services.credential import Credential
from onvif.services.deviceio import DeviceIO
from onvif.services.devicemgmt import Device
from onvif.services.display import Display
from onvif.services.doorcontrol import DoorControl
from onvif.services.events.events import Events
from onvif.services.events.notification import Notification
from onvif.services.events.pausable_subscription import PausableSubscription
from onvif.services.events.pullpoint import PullPoint
from onvif.services.events.subscription import Subscription
from onvif.services.imaging import Imaging
from onvif.services.media import Media
from onvif.services.media2 import Media2
from onvif.services.provisioning import Provisioning
from onvif.services.ptz import PTZ
from onvif.services.receiver import Receiver
from onvif.services.recording import Recording
from onvif.services.replay import Replay
from onvif.services.schedule import Schedule
from onvif.services.search import Search
from onvif.services.security.advancedsecurity import AdvancedSecurity
from onvif.services.security.authorizationserver import AuthorizationServer
from onvif.services.security.dot1x import Dot1X
from onvif.services.security.jwt import JWT
from onvif.services.security.keystore import Keystore
from onvif.services.security.mediasigning import MediaSigning
from onvif.services.security.tlsserver import TLSServer
from onvif.services.thermal import Thermal
from onvif.services.uplink import Uplink

__all__ = [
    "Device",
    "Events",
    "PullPoint",
    "Notification",
    "Subscription",
    "PausableSubscription",
    "Imaging",
    "Media",
    "Media2",
    "PTZ",
    "AccessControl",
    "AccessRules",
    "ActionEngine",
    "Analytics",
    "RuleEngine",
    "AnalyticsDevice",
    "AppManagement",
    "AuthenticationBehavior",
    "Credential",
    "DeviceIO",
    "Display",
    "DoorControl",
    "Provisioning",
    "Receiver",
    "Recording",
    "Replay",
    "Schedule",
    "Search",
    "Thermal",
    "Uplink",
    "AdvancedSecurity",
    "JWT",
    "Keystore",
    "TLSServer",
    "Dot1X",
    "AuthorizationServer",
    "MediaSigning",
]
