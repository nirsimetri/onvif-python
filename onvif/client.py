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
from .utils import ONVIFWSDL, ZeepPatcher, XMLCapturePlugin


class ONVIFClient:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout: int = 10,
        cache: CacheMode = CacheMode.ALL,
        use_https: bool = False,
        verify_ssl: bool = True,
        apply_patch: bool = True,
        capture_xml: bool = False,
        wsdl_dir: str = None,
    ):
        # Apply or remove zeep patch based on user preference
        if apply_patch:
            ZeepPatcher.apply_patch()
        else:
            ZeepPatcher.remove_patch()

        # Initialize XML capture plugin if requested
        self.xml_plugin = None
        if capture_xml:
            self.xml_plugin = XMLCapturePlugin()

        # Store custom WSDL directory if provided
        self.wsdl_dir = wsdl_dir
        if wsdl_dir:
            ONVIFWSDL.set_custom_wsdl_dir(wsdl_dir)

        # Pass to ONVIFOperator
        self.common_args = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "timeout": timeout,
            "cache": cache,
            "use_https": use_https,
            "verify_ssl": verify_ssl,
            "apply_patch": apply_patch,
            "plugins": [self.xml_plugin] if self.xml_plugin else None,
        }

        # Device Management (Core) service is always available
        self._devicemgmt = Device(**self.common_args)

        # Try to retrieve device services and create namespace -> XAddr mapping
        self.services = None
        self._service_map = {}

        # Temporary variable to hold capabilities
        self.capabilities = None

        try:
            # Try GetServices first (preferred method)
            self.services = self._devicemgmt.GetServices(IncludeCapability=False)
            for service in self.services:
                namespace = getattr(service, "Namespace", None)
                xaddr = getattr(service, "XAddr", None)

                if namespace and xaddr:
                    self._service_map[namespace] = xaddr

        except Exception:
            # Fallback to GetCapabilities if GetServices is not supported on device
            try:
                self.capabilities = self._devicemgmt.GetCapabilities(Category="All")
            except Exception:
                # If both fail, we'll use default URLs
                pass

        # Lazy init for other services

        self._events = None
        self._pullpoints = {}  # Dictionary for multiple PullPoint instances
        self._notification = None
        self._subscriptions = {}  # Dictionary for multiple Subscription instances

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
        Resolve XAddr for ONVIF services using a comprehensive 3-tier discovery approach.

        1. GetServices: Try to resolve from GetServices response using namespace mapping
        2. GetCapabilities: Fall back to GetCapabilities response with multiple lookup strategies:
           - Direct capabilities.service_path
           - Extension capabilities.Extension.service_path
           - Nested Extension capabilities.Extension.Extensions.service_path
        3. Default URL: Generate default ONVIF URL as final fallback

        Args:
            service_name: Internal service name (e.g., 'imaging', 'media', 'deviceio')
            service_path: ONVIF service path (e.g., 'Imaging', 'Media', 'DeviceIO')

        Returns:
            str: The resolved XAddr URL for the service

        Notes:
            - GetServices is the preferred method as it provides the most accurate service endpoints.
              But not all devices implement it because it's optional in the ONVIF spec.
            - GetCapabilities lookup tries multiple strategies to maximize chances of finding the XAddr.
              And GetCapabilities is mandatory for ONVIF devices, so it's more widely supported.
            - Fallback to default URL ensures basic connectivity even if the device lacks proper service discovery.
        """

        # First try to get from GetServices mapping
        if self.services:
            # Get the namespace for this service from WSDL_MAP
            try:
                # Try to get the service definition from WSDL_MAP
                # Most services use ver10, some use ver20
                wsdl_def = None

                # Try ver10 first, then ver20
                if service_name in ONVIFWSDL.WSDL_MAP:
                    if "ver10" in ONVIFWSDL.WSDL_MAP[service_name]:
                        wsdl_def = ONVIFWSDL.WSDL_MAP[service_name]["ver10"]
                    elif "ver20" in ONVIFWSDL.WSDL_MAP[service_name]:
                        wsdl_def = ONVIFWSDL.WSDL_MAP[service_name]["ver20"]

                if wsdl_def:
                    namespace = wsdl_def["namespace"]
                    xaddr = self._service_map.get(namespace)

                    if xaddr:
                        # Rewrite host/port if needed
                        rewritten = self._rewrite_xaddr_if_needed(xaddr)
                        return rewritten
            except Exception:
                pass

        # If not found in service map and we have capabilities, try to get it dynamically from GetCapabilities
        if self.capabilities:
            try:
                svc = getattr(self.capabilities, service_path, None)
                # Step 1: check direct attribute capabilities.service_path (e.g. capabilities.Media)
                if svc and hasattr(svc, "XAddr"):
                    xaddr = svc.XAddr
                else:
                    # Step 2: try capabilities.Extension.service_path (e.g. capabilities.Extension.DeviceIO)
                    ext = getattr(self.capabilities, "Extension", None)
                    if ext and hasattr(ext, service_path):
                        svc = getattr(ext, service_path, None)
                        xaddr = getattr(svc, "XAddr", None) if svc else None
                    else:
                        # Step 3: try capabilities.Extension.Extensions.service_path
                        # (e.g. capabilities.Extension.Extensions.Provisioning)
                        ext_ext = getattr(ext, "Extensions", None)
                        if ext_ext and hasattr(ext_ext, service_path):
                            svc = getattr(ext_ext, service_path, None)
                            xaddr = getattr(svc, "XAddr", None) if svc else None

                if xaddr:
                    # Rewrite host/port if needed
                    rewritten = self._rewrite_xaddr_if_needed(xaddr)
                    return rewritten
            except Exception:
                pass

        # Fallback to default URL
        protocol = "https" if self.common_args["use_https"] else "http"
        return f"{protocol}://{self.common_args['host']}:{self.common_args['port']}/onvif/{service_path}"

    def _rewrite_xaddr_if_needed(self, xaddr: str):
        """
        Rewrite XAddr to use client's host/port if different from device's.
        """
        try:
            parsed = urlparse(xaddr)
            device_host = parsed.hostname
            device_port = parsed.port
            connect_host = self.common_args["host"]
            connect_port = self.common_args["port"]

            if (device_host != connect_host) or (device_port != connect_port):
                protocol = "https" if self.common_args["use_https"] else "http"
                new_netloc = f"{connect_host}:{connect_port}"
                return urlunparse((protocol, new_netloc, parsed.path, "", "", ""))
            return xaddr
        except Exception:
            return xaddr

    # Core (Device Management)

    def devicemgmt(self):
        return self._devicemgmt

    # Core (Events)

    def events(self):
        if self._events is None:
            self._events = Events(
                xaddr=self._get_xaddr("events", "Events"), **self.common_args
            )
        return self._events

    def pullpoint(self, SubscriptionRef):
        xaddr = None
        try:
            addr_obj = SubscriptionRef["SubscriptionReference"]["Address"]
            if isinstance(addr_obj, dict) and "_value_1" in addr_obj:
                xaddr = addr_obj["_value_1"]
            elif hasattr(addr_obj, "_value_1"):
                xaddr = addr_obj._value_1

            xaddr = self._rewrite_xaddr_if_needed(xaddr)
        except Exception:
            pass

        if not xaddr:
            raise RuntimeError(
                "SubscriptionReference.Address missing in subscription response"
            )

        if xaddr not in self._pullpoints:
            self._pullpoints[xaddr] = PullPoint(xaddr=xaddr, **self.common_args)

        return self._pullpoints[xaddr]

    def notification(self):
        if self._notification is None:
            self._notification = Notification(
                xaddr=self._get_xaddr("notification", "Events"), **self.common_args
            )
        return self._notification

    def subscription(self, SubscriptionRef):
        xaddr = None
        try:
            addr_obj = SubscriptionRef["SubscriptionReference"]["Address"]
            if isinstance(addr_obj, dict) and "_value_1" in addr_obj:
                xaddr = addr_obj["_value_1"]
            elif hasattr(addr_obj, "_value_1"):
                xaddr = addr_obj._value_1

            xaddr = self._rewrite_xaddr_if_needed(xaddr)
        except Exception:
            pass

        if not xaddr:
            raise RuntimeError(
                "SubscriptionReference.Address missing in subscription response"
            )

        if xaddr not in self._subscriptions:
            self._subscriptions[xaddr] = Subscription(xaddr=xaddr, **self.common_args)

        return self._subscriptions[xaddr]

    # Imaging

    def imaging(self):
        if self._imaging is None:
            self._imaging = Imaging(
                xaddr=self._get_xaddr("imaging", "Imaging"), **self.common_args
            )
        return self._imaging

    # Media

    def media(self):
        if self._media is None:
            self._media = Media(
                xaddr=self._get_xaddr("media", "Media"), **self.common_args
            )
        return self._media

    def media2(self):
        if self._media2 is None:
            self._media2 = Media2(
                xaddr=self._get_xaddr("media2", "Media2"), **self.common_args
            )
        return self._media2

    # PTZ

    def ptz(self):
        if self._ptz is None:
            self._ptz = PTZ(xaddr=self._get_xaddr("ptz", "PTZ"), **self.common_args)
        return self._ptz

    # DeviceIO

    def deviceio(self):
        if self._deviceio is None:
            self._deviceio = DeviceIO(
                xaddr=self._get_xaddr("deviceio", "DeviceIO"), **self.common_args
            )
        return self._deviceio

    # Display

    def display(self):
        if self._display is None:
            self._display = Display(
                xaddr=self._get_xaddr("display", "Display"), **self.common_args
            )
        return self._display

    # Analytics

    def analytics(self):
        if self._analytics is None:
            self._analytics = Analytics(
                xaddr=self._get_xaddr("analytics", "Analytics"), **self.common_args
            )
        return self._analytics

    def ruleengine(self):
        if self._ruleengine is None:
            self._ruleengine = RuleEngine(
                xaddr=self._get_xaddr("ruleengine", "Analytics"), **self.common_args
            )
        return self._ruleengine

    def analyticsdevice(self):
        if self._analyticsdevice is None:
            self._analyticsdevice = AnalyticsDevice(
                xaddr=self._get_xaddr("analyticsdevice", "AnalyticsDevice"),
                **self.common_args,
            )
        return self._analyticsdevice

    # PACS

    def accesscontrol(self):
        if self._accesscontrol is None:
            self._accesscontrol = AccessControl(
                xaddr=self._get_xaddr("accesscontrol", "AccessControl"),
                **self.common_args,
            )
        return self._accesscontrol

    def doorcontrol(self):
        if self._doorcontrol is None:
            self._doorcontrol = DoorControl(
                xaddr=self._get_xaddr("doorcontrol", "DoorControl"), **self.common_args
            )
        return self._doorcontrol

    # AccessRules

    def accessrules(self):
        if self._accessrules is None:
            self._accessrules = AccessRules(
                xaddr=self._get_xaddr("accessrules", "AccessRules"), **self.common_args
            )
        return self._accessrules

    # ActionEngine

    def actionengine(self):
        if self._actionengine is None:
            self._actionengine = ActionEngine(
                xaddr=self._get_xaddr("actionengine", "ActionEngine"),
                **self.common_args,
            )
        return self._actionengine

    # AppManagement

    def appmanagement(self):
        if self._appmanagement is None:
            self._appmanagement = AppManagement(
                xaddr=self._get_xaddr("appmgmt", "AppManagement"),
                **self.common_args,
            )
        return self._appmanagement

    # AuthenticationBehavior

    def authenticationbehavior(self):
        if self._authenticationbehavior is None:
            self._authenticationbehavior = AuthenticationBehavior(
                xaddr=self._get_xaddr(
                    "authenticationbehavior", "AuthenticationBehavior"
                ),
                **self.common_args,
            )
        return self._authenticationbehavior

    # Credential

    def credential(self):
        if self._credential is None:
            self._credential = Credential(
                xaddr=self._get_xaddr("credential", "Credential"),
                **self.common_args,
            )
        return self._credential

    # Recording

    def recording(self):
        if self._recording is None:
            self._recording = Recording(
                xaddr=self._get_xaddr("recording", "Recording"),
                **self.common_args,
            )
        return self._recording

    # Replay

    def replay(self):
        if self._replay is None:
            self._replay = Replay(
                xaddr=self._get_xaddr("replay", "Replay"),
                **self.common_args,
            )
        return self._replay

    # Provisioning

    def provisioning(self):
        if self._provisioning is None:
            self._provisioning = Provisioning(
                xaddr=self._get_xaddr("provisioning", "Provisioning"),
                **self.common_args,
            )
        return self._provisioning

    # Receiver

    def receiver(self):
        if self._receiver is None:
            self._receiver = Receiver(
                xaddr=self._get_xaddr("receiver", "Receiver"),
                **self.common_args,
            )
        return self._receiver

    # Schedule

    def schedule(self):
        if self._schedule is None:
            self._schedule = Schedule(
                xaddr=self._get_xaddr("schedule", "Schedule"),
                **self.common_args,
            )
        return self._schedule

    # Search

    def search(self):
        if self._search is None:
            self._search = Search(
                xaddr=self._get_xaddr("search", "Search"),
                **self.common_args,
            )
        return self._search

    # Thermal

    def thermal(self):
        if self._thermal is None:
            self._thermal = Thermal(
                xaddr=self._get_xaddr("thermal", "Thermal"),
                **self.common_args,
            )
        return self._thermal

    # Uplink

    def uplink(self):
        if self._uplink is None:
            self._uplink = Uplink(
                xaddr=self._get_xaddr("uplink", "Uplink"),
                **self.common_args,
            )
        return self._uplink

    # Security - AdvancedSecurity

    def security(self):
        if self._security is None:
            self._security = AdvancedSecurity(
                xaddr=self._get_xaddr("advancedsecurity", "Security"),
                **self.common_args,
            )
        return self._security

    def jwt(self, xaddr):
        if self._jwt is None:
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._jwt = JWT(xaddr=xaddr, **self.common_args)
        return self._jwt

    def keystore(self, xaddr):
        if self._keystore is None:
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._keystore = Keystore(xaddr=xaddr, **self.common_args)
        return self._keystore

    def tlsserver(self, xaddr):
        if self._tlsserver is None:
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._tlsserver = TLSServer(xaddr=xaddr, **self.common_args)
        return self._tlsserver

    def dot1x(self, xaddr):
        if self._dot1x is None:
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._dot1x = Dot1X(xaddr=xaddr, **self.common_args)
        return self._dot1x

    def authorizationserver(self, xaddr):
        if self._authorizationserver is None:
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._authorizationserver = AuthorizationServer(
                xaddr=xaddr, **self.common_args
            )
        return self._authorizationserver

    def mediasigning(self, xaddr):
        if self._mediasigning is None:
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._mediasigning = MediaSigning(xaddr=xaddr, **self.common_args)
        return self._mediasigning
