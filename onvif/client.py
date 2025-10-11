# onvif/client.py

from urllib.parse import urlparse, urlunparse

from .services import (
    Device,
    Events,
    PullPoint,
    Notification,
    Subscription,
    Imaging,
    Media,
    Media2,
    PTZ,
    DeviceIO,
    AccessControl,
    AccessRules,
    ActionEngine,
    Analytics,
    RuleEngine,
    AnalyticsDevice,
    AppManagement,
    AuthenticationBehavior,
    Credential,
    Recording,
    Replay,
    Display,
    DoorControl,
    Provisioning,
    Receiver,
    Schedule,
    Search,
    Thermal,
    Uplink,
    AdvancedSecurity,
    JWT,
    Keystore,
    TLSServer,
    Dot1X,
    AuthorizationServer,
    MediaSigning,
)
from .operator import CacheMode
from .utils.zeep import (
    apply_patch as _apply_zeep_patch,
    remove_patch as _remove_zeep_patch,
)


class ONVIFClient:
    def __init__(
        self,
        host,
        port,
        username,
        password,
        timeout=10,
        cache=CacheMode.ALL,
        use_https=False,
        verify_ssl=True,
        apply_patch=True,
    ):
        self.apply_patch = apply_patch

        # Apply or remove zeep patch based on user preference
        if apply_patch:
            _apply_zeep_patch()
        else:
            _remove_zeep_patch()

        self.common_args = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "timeout": timeout,
            "cache": cache,
            "use_https": use_https,
            "verify_ssl": verify_ssl,
            "apply_flatten": apply_patch,  # Pass to ONVIFOperator
        }

        # Device Management (Core) service is always available
        self._devicemgmt = Device(**self.common_args)

        # Retrieve device capabilities once and reuse
        self.capabilities = self._devicemgmt.GetCapabilities(Category="All")

        # Lazy init for other services

        self._events = None
        self._pullpoint = None
        self._notification = None
        self._subscription = None

        self._imaging = None

        self._media = None
        self._media2 = None

        self._ptz = None

        self._deviceio = None

        self._display = None

        self._analytics = None
        self._ruleengine = None
        self._analyticsdevice = None

        self._accesscontrol = None
        self._doorcontrol = None

        self._accessrules = None

        self._actionengine = None

        self._appmanagement = None

        self._authenticationbehavior = None

        self._credential = None

        self._recording = None
        self._replay = None

        self._provisioning = None

        self._receiver = None

        self._schedule = None

        self._search = None

        self._thermal = None

        self._uplink = None

        self._security = None
        self._jwt = None
        self._keystore = None
        self._tlsserver = None
        self._dot1x = None
        self._authorizationserver = None
        self._mediasigning = None

    def _get_xaddr(self, service_name: str, service_path: str):
        """
        Resolve XAddr from GetCapabilities. Fallback to default if not present.
        Now supports nested Extension with _value_1 dict (after normalized parsing).
        """
        svc = getattr(self.capabilities, service_name, None)

        # Step 1: check direct attribute (e.g. capabilities.Media)
        if svc and hasattr(svc, "XAddr"):
            xaddr = svc.XAddr
        else:
            # Step 2: try legacy Extension.service_name
            ext = getattr(self.capabilities, "Extension", None)
            if ext and hasattr(ext, service_name):
                svc = getattr(ext, service_name, None)
                xaddr = getattr(svc, "XAddr", None) if svc else None
            else:
                # Step 3: try new-style _value_1 dict inside Extension
                ext_dict = getattr(ext, "_value_1", {})
                xaddr = (
                    ext_dict.get(service_name, {}).get("XAddr")
                    if isinstance(ext_dict, dict)
                    else None
                )

        if xaddr:
            parsed = urlparse(xaddr)
            # Host/port from device
            device_host = parsed.hostname
            device_port = parsed.port
            # Host/port from connection
            connect_host = self.common_args["host"]
            connect_port = self.common_args["port"]
            # if host/port differ, rewrite XAddr to use connection values
            if (device_host != connect_host) or (device_port != connect_port):
                protocol = "https" if self.common_args["use_https"] else "http"
                new_netloc = f"{connect_host}:{connect_port}"
                rewritten = urlunparse((protocol, new_netloc, parsed.path, "", "", ""))
                return rewritten
            return xaddr

        # Fallback default
        protocol = "https" if self.common_args["use_https"] else "http"
        return f"{protocol}://{self.common_args['host']}:{self.common_args['port']}/onvif/{service_path}"

    # Core (Device Management)

    def devicemgmt(self):
        return self._devicemgmt

    # Core (Events)

    def events(self):
        if self._events is None:
            self._events = Events(
                xaddr=self._get_xaddr("Events", "Events"), **self.common_args
            )
        return self._events

    def pullpoint(self, SubscriptionRef):
        if self._pullpoint is None:
            xaddr = None
            try:
                addr_obj = SubscriptionRef["SubscriptionReference"]["Address"]
                if isinstance(addr_obj, dict) and "_value_1" in addr_obj:
                    xaddr = addr_obj["_value_1"]
                elif hasattr(addr_obj, "_value_1"):
                    xaddr = addr_obj._value_1
            except Exception:
                pass

            if not xaddr:
                raise RuntimeError(
                    "SubscriptionReference.Address missing in subscription response"
                )

            self._pullpoint = PullPoint(xaddr=xaddr, **self.common_args)
        return self._pullpoint

    def notification(self):
        if self._notification is None:
            self._notification = Notification(
                xaddr=self._get_xaddr("Events", "Events"), **self.common_args
            )
        return self._notification

    def subscription(self, SubscriptionRef):
        if self._subscription is None:
            xaddr = None
            try:
                addr_obj = SubscriptionRef["SubscriptionReference"]["Address"]
                if isinstance(addr_obj, dict) and "_value_1" in addr_obj:
                    xaddr = addr_obj["_value_1"]
                elif hasattr(addr_obj, "_value_1"):
                    xaddr = addr_obj._value_1
            except Exception:
                pass

            if not xaddr:
                raise RuntimeError(
                    "SubscriptionReference.Address missing in subscription response"
                )

            self._subscription = Subscription(xaddr=xaddr, **self.common_args)
        return self._subscription

    # Imaging

    def imaging(self):
        if self._imaging is None:
            self._imaging = Imaging(
                xaddr=self._get_xaddr("Imaging", "Imaging"), **self.common_args
            )
        return self._imaging

    # Media

    def media(self):
        if self._media is None:
            self._media = Media(
                xaddr=self._get_xaddr("Media", "Media"), **self.common_args
            )
        return self._media

    def media2(self):
        if self._media2 is None:
            self._media2 = Media2(
                xaddr=self._get_xaddr("Media2", "Media2"), **self.common_args
            )
        return self._media2

    # PTZ

    def ptz(self):
        if self._ptz is None:
            self._ptz = PTZ(xaddr=self._get_xaddr("PTZ", "PTZ"), **self.common_args)
        return self._ptz

    # DeviceIO

    def deviceio(self):
        if self._deviceio is None:
            self._deviceio = DeviceIO(
                xaddr=self._get_xaddr("DeviceIO", "DeviceIO"), **self.common_args
            )
        return self._deviceio

    # Display

    def display(self):
        if self._display is None:
            self._display = Display(
                xaddr=self._get_xaddr("Display", "Display"), **self.common_args
            )
        return self._display

    # Analytics

    def analytics(self):
        if self._analytics is None:
            self._analytics = Analytics(
                xaddr=self._get_xaddr("Analytics", "Analytics"), **self.common_args
            )
        return self._analytics

    def ruleengine(self):
        if self._ruleengine is None:
            self._ruleengine = RuleEngine(
                xaddr=self._get_xaddr("Analytics", "Analytics"), **self.common_args
            )
        return self._ruleengine

    def analyticsdevice(self):
        if self._analyticsdevice is None:
            self._analyticsdevice = AnalyticsDevice(
                xaddr=self._get_xaddr("AnalyticsDevice", "AnalyticsDevice"),
                **self.common_args,
            )
        return self._analyticsdevice

    # PACS

    def accesscontrol(self):
        if self._accesscontrol is None:
            self._accesscontrol = AccessControl(
                xaddr=self._get_xaddr("AccessControl", "AccessControl"),
                **self.common_args,
            )
        return self._accesscontrol

    def doorcontrol(self):
        if self._doorcontrol is None:
            self._doorcontrol = DoorControl(
                xaddr=self._get_xaddr("DoorControl", "DoorControl"), **self.common_args
            )
        return self._doorcontrol

    # AccessRules

    def accessrules(self):
        if self._accessrules is None:
            self._accessrules = AccessRules(
                xaddr=self._get_xaddr("AccessRules", "AccessRules"), **self.common_args
            )
        return self._accessrules

    # ActionEngine

    def actionengine(self):
        if self._actionengine is None:
            self._actionengine = ActionEngine(
                xaddr=self._get_xaddr("ActionEngine", "ActionEngine"),
                **self.common_args,
            )
        return self._actionengine

    # AppManagement

    def appmanagement(self):
        if self._appmanagement is None:
            self._appmanagement = AppManagement(
                xaddr=self._get_xaddr("AppManagement", "AppManagement"),
                **self.common_args,
            )
        return self._appmanagement

    # AuthenticationBehavior

    def authenticationbehavior(self):
        if self._authenticationbehavior is None:
            self._authenticationbehavior = AuthenticationBehavior(
                xaddr=self._get_xaddr(
                    "AuthenticationBehavior", "AuthenticationBehavior"
                ),
                **self.common_args,
            )
        return self._authenticationbehavior

    # Credential

    def credential(self):
        if self._credential is None:
            self._credential = Credential(
                xaddr=self._get_xaddr("Credential", "Credential"),
                **self.common_args,
            )
        return self._credential

    # Recording

    def recording(self):
        if self._recording is None:
            self._recording = Recording(
                xaddr=self._get_xaddr("Recording", "Recording"),
                **self.common_args,
            )
        return self._recording

    # Replay

    def replay(self):
        if self._replay is None:
            self._replay = Replay(
                xaddr=self._get_xaddr("Replay", "Replay"),
                **self.common_args,
            )
        return self._replay

    # Provisioning

    def provisioning(self):
        if self._provisioning is None:
            self._provisioning = Provisioning(
                xaddr=self._get_xaddr("Provisioning", "Provisioning"),
                **self.common_args,
            )
        return self._provisioning

    # Receiver

    def receiver(self):
        if self._receiver is None:
            self._receiver = Receiver(
                xaddr=self._get_xaddr("Receiver", "Receiver"),
                **self.common_args,
            )
        return self._receiver

    # Schedule

    def schedule(self):
        if self._schedule is None:
            self._schedule = Schedule(
                xaddr=self._get_xaddr("Schedule", "Schedule"),
                **self.common_args,
            )
        return self._schedule

    # Search

    def search(self):
        if self._search is None:
            self._search = Search(
                xaddr=self._get_xaddr("Search", "Search"),
                **self.common_args,
            )
        return self._search

    # Thermal

    def thermal(self):
        if self._thermal is None:
            self._thermal = Thermal(
                xaddr=self._get_xaddr("Thermal", "Thermal"),
                **self.common_args,
            )
        return self._thermal

    # Uplink

    def uplink(self):
        if self._uplink is None:
            self._uplink = Uplink(
                xaddr=self._get_xaddr("Uplink", "Uplink"),
                **self.common_args,
            )
        return self._uplink

    # Security - AdvancedSecurity

    def security(self):
        if self._security is None:
            self._security = AdvancedSecurity(
                xaddr=self._get_xaddr("Security", "Security"),
                **self.common_args,
            )
        return self._security

    def jwt(self, xaddr):
        if self._jwt is None:
            self._jwt = JWT(xaddr=xaddr, **self.common_args)
        return self._jwt

    def keystore(self, xaddr):
        if self._keystore is None:
            self._keystore = Keystore(xaddr=xaddr, **self.common_args)
        return self._keystore

    def tlsserver(self, xaddr):
        if self._tlsserver is None:
            self._tlsserver = TLSServer(xaddr=xaddr, **self.common_args)
        return self._tlsserver

    def dot1x(self, xaddr):
        if self._dot1x is None:
            self._dot1x = Dot1X(xaddr=xaddr, **self.common_args)
        return self._dot1x

    def authorizationserver(self, xaddr):
        if self._authorizationserver is None:
            self._authorizationserver = AuthorizationServer(
                xaddr=xaddr, **self.common_args
            )
        return self._authorizationserver

    def mediasigning(self, xaddr):
        if self._mediasigning is None:
            self._mediasigning = MediaSigning(xaddr=xaddr, **self.common_args)
        return self._mediasigning
