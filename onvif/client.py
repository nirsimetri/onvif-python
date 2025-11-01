# onvif/client.py

from urllib.parse import urlparse, urlunparse
from functools import wraps
import logging

from .services import (
    Device,
    Events,
    PullPoint,
    Notification,
    Subscription,
    PausableSubscription,
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
from .utils import ONVIFWSDL, ZeepPatcher, XMLCapturePlugin, ONVIFOperationException

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def service(func):
    """Decorator to wrap service accessor methods with ONVIFOperationException handling.

    This decorator catches any exception raised during service initialization and
    wraps it in ONVIFOperationException for consistent error handling across all
    ONVIF client service accessors.

    Args:
        func: Service accessor method to wrap

    Returns:
        Wrapped function that handles exceptions

    Raises:
        ONVIFOperationException: If service initialization fails
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except ONVIFOperationException as oe:
            # Re-raise ONVIFOperationException as-is to avoid double-wrapping
            logger.error(f"Service initialization failed in {func.__name__}: {oe}")
            raise
        except Exception as e:
            # Wrap any other exception in ONVIFOperationException
            logger.error(f"Service initialization failed in {func.__name__}: {e}")
            raise ONVIFOperationException(func.__name__, e)

    return wrapper


class ONVIFClient:
    """ONVIF Client for communicating with ONVIF-compliant devices.

    This is the main class for interacting with ONVIF devices. It provides access to
    all ONVIF services including Device Management, Media, PTZ, Events, Analytics, and more.

    The client automatically discovers available services on the device using GetServices
    or GetCapabilities, and provides lazy initialization for service endpoints.

    Attributes:
        services: List of available services from GetServices response
        capabilities: Device capabilities from GetCapabilities response (fallback)
        xml_plugin: XML capture plugin for debugging (if capture_xml=True)
        wsdl_dir: Custom WSDL directory path (if provided)
    """

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
        plugins: list = None,
    ):
        logger.info(f"Initializing ONVIF client for {host}:{port}")
        logger.debug(
            f"Connection settings: HTTPS={use_https}, SSL_verify={verify_ssl}, cache={cache.value}, timeout={timeout}s"
        )

        # Apply or remove zeep patch based on user preference
        if apply_patch:
            logger.debug("Applying ZeepPatcher")
            ZeepPatcher.apply_patch()
        else:
            logger.debug("Removing ZeepPatcher")
            ZeepPatcher.remove_patch()

        # Initialize XML capture plugin if requested
        self.xml_plugin = None
        if capture_xml:
            logger.debug("Enabling XML capture plugin")
            self.xml_plugin = XMLCapturePlugin()

        # Merge user plugins with xml_plugin
        all_plugins = []
        if plugins:
            logger.debug(f"Adding {len(plugins)} user-provided plugins")
            all_plugins.extend(plugins)
        if self.xml_plugin:
            logger.debug("Adding XML capture plugin")
            all_plugins.append(self.xml_plugin)

        # Store custom WSDL directory if provided
        self.wsdl_dir = wsdl_dir
        if wsdl_dir:
            logger.debug(f"Using custom WSDL directory: {wsdl_dir}")
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
            "plugins": all_plugins if all_plugins else None,
        }

        # Device Management (Core) service is always available
        self._devicemgmt = None
        self._devicemgmt = self.devicemgmt()

        # Try to retrieve device services and create namespace -> XAddr mapping
        self.services = None
        self._service_map = {}

        # Temporary variable to hold capabilities
        self.capabilities = None

        # Cache for security service capabilities (lazy loaded)
        self._security_capabilities = None
        self._security_capabilities_checked = False

        # Cache for JWT service availability (lazy loaded)
        self._jwt_available = None
        self._jwt_checked = False

        try:
            # Try GetServices first (preferred method)
            logger.debug("Attempting GetServices call for service discovery")
            self.services = self._devicemgmt.GetServices(IncludeCapability=False)
            logger.info(f"Found {len(self.services)} services via GetServices")

            for service in self.services:
                namespace = getattr(service, "Namespace", None)
                xaddr = getattr(service, "XAddr", None)

                if namespace and xaddr:
                    self._service_map[namespace] = xaddr
                    logger.debug(f"Mapped service: {namespace} -> {xaddr}")

        except Exception as e:
            logger.warning(f"GetServices failed: {e}")
            # Fallback to GetCapabilities if GetServices is not supported on device
            try:
                logger.debug("Falling back to GetCapabilities")
                self.capabilities = self._devicemgmt.GetCapabilities(Category="All")
                logger.info("Successfully retrieved device capabilities")
            except Exception as e2:
                # If both fail, we'll use default URLs
                logger.error(f"Both GetServices and GetCapabilities failed: {e2}")
                logger.warning("Using default URLs for services")
                pass

        # Lazy init for other services

        self._events = None
        self._pullpoints = {}  # Dictionary for multiple PullPoint instances
        self._notification = None
        self._subscriptions = {}  # Dictionary for multiple Subscription instances
        self._pausable_subscriptions = (
            {}
        )  # Dictionary for multiple PausableSubscription instances

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
        logger.debug(f"Resolving XAddr for service: {service_name} ({service_path})")

        # First try to get from GetServices mapping
        if self.services:
            logger.debug("Attempting resolution via GetServices")
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
                        logger.debug(
                            f"Resolved via GetServices: {service_name} -> {rewritten}"
                        )
                        return rewritten
            except Exception as e:
                logger.debug(
                    f"Service {service_name} not found in GetServices mapping: {e}"
                )
                pass

        # If not found in service map and we have capabilities, try to get it dynamically from GetCapabilities
        if self.capabilities:
            logger.debug("Attempting resolution via GetCapabilities")
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
                    logger.debug(
                        f"Resolved via GetCapabilities: {service_name} -> {rewritten}"
                    )
                    return rewritten
            except Exception as e:
                logger.debug(
                    f"Service {service_name} not found in GetCapabilities mapping: {e}"
                )
                pass

        # Fallback to default URL
        protocol = "https" if self.common_args["use_https"] else "http"
        default_url = f"{protocol}://{self.common_args['host']}:{self.common_args['port']}/onvif/{service_path}"
        logger.warning(f"Using default URL for {service_name}: {default_url}")
        return default_url

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
                rewritten = urlunparse((protocol, new_netloc, parsed.path, "", "", ""))
                logger.debug(f"Rewritten XAddr: {xaddr} -> {rewritten}")
                return rewritten

            logger.debug(f"XAddr unchanged: {xaddr}")
            return xaddr
        except Exception as e:
            logger.warning(f"Failed to parse XAddr {xaddr}, returning as-is: {e}")
            return xaddr

    # Core (Device Management)

    @service
    def devicemgmt(self):
        if self._devicemgmt is None:
            logger.debug("Initializing Device Management service")
            self._devicemgmt = Device(**self.common_args)
        return self._devicemgmt

    # Core (Events)

    @service
    def events(self):
        if self._events is None:
            logger.debug("Initializing Events service")
            self._events = Events(
                xaddr=self._get_xaddr("events", "Events"), **self.common_args
            )
        return self._events

    @service
    def pullpoint(self, SubscriptionRef):
        logger.debug("Initializing PullPoint service")
        xaddr = None
        addr_obj = SubscriptionRef["SubscriptionReference"]["Address"]
        if isinstance(addr_obj, dict) and "_value_1" in addr_obj:
            xaddr = addr_obj["_value_1"]
        elif hasattr(addr_obj, "_value_1"):
            xaddr = addr_obj._value_1

        xaddr = self._rewrite_xaddr_if_needed(xaddr)

        if not xaddr:
            raise RuntimeError(
                "SubscriptionReference.Address missing in subscription response"
            )

        if xaddr not in self._pullpoints:
            self._pullpoints[xaddr] = PullPoint(xaddr=xaddr, **self.common_args)

        return self._pullpoints[xaddr]

    @service
    def notification(self):
        if self._notification is None:
            logger.debug("Initializing Notification service")
            self._notification = Notification(
                xaddr=self._get_xaddr("notification", "Events"), **self.common_args
            )
        return self._notification

    @service
    def subscription(self, SubscriptionRef):
        logger.debug("Initializing Subscription service")
        xaddr = None
        addr_obj = SubscriptionRef["SubscriptionReference"]["Address"]
        if isinstance(addr_obj, dict) and "_value_1" in addr_obj:
            xaddr = addr_obj["_value_1"]
        elif hasattr(addr_obj, "_value_1"):
            xaddr = addr_obj._value_1

        xaddr = self._rewrite_xaddr_if_needed(xaddr)

        if not xaddr:
            raise RuntimeError(
                "SubscriptionReference.Address missing in subscription response"
            )

        if xaddr not in self._subscriptions:
            self._subscriptions[xaddr] = Subscription(xaddr=xaddr, **self.common_args)

        return self._subscriptions[xaddr]

    @service
    def pausable_subscription(self, SubscriptionRef):
        logger.debug("Initializing PausableSubscription service")
        xaddr = None
        addr_obj = SubscriptionRef["SubscriptionReference"]["Address"]
        if isinstance(addr_obj, dict) and "_value_1" in addr_obj:
            xaddr = addr_obj["_value_1"]
        elif hasattr(addr_obj, "_value_1"):
            xaddr = addr_obj._value_1

        xaddr = self._rewrite_xaddr_if_needed(xaddr)

        if not xaddr:
            raise RuntimeError(
                "SubscriptionReference.Address missing in subscription response"
            )

        if xaddr not in self._pausable_subscriptions:
            self._pausable_subscriptions[xaddr] = PausableSubscription(
                xaddr=xaddr, **self.common_args
            )

        return self._pausable_subscriptions[xaddr]

    # Imaging

    @service
    def imaging(self):
        if self._imaging is None:
            logger.debug("Initializing Imaging service")
            self._imaging = Imaging(
                xaddr=self._get_xaddr("imaging", "Imaging"), **self.common_args
            )
        return self._imaging

    # Media

    @service
    def media(self):
        if self._media is None:
            logger.debug("Initializing Media service")
            self._media = Media(
                xaddr=self._get_xaddr("media", "Media"), **self.common_args
            )
        return self._media

    @service
    def media2(self):
        if self._media2 is None:
            logger.debug("Initializing Media2 service")
            self._media2 = Media2(
                xaddr=self._get_xaddr("media2", "Media2"), **self.common_args
            )
        return self._media2

    # PTZ

    @service
    def ptz(self):
        if self._ptz is None:
            logger.debug("Initializing PTZ service")
            self._ptz = PTZ(xaddr=self._get_xaddr("ptz", "PTZ"), **self.common_args)
        return self._ptz

    # DeviceIO

    @service
    def deviceio(self):
        if self._deviceio is None:
            logger.debug("Initializing DeviceIO service")
            self._deviceio = DeviceIO(
                xaddr=self._get_xaddr("deviceio", "DeviceIO"), **self.common_args
            )
        return self._deviceio

    # Display

    @service
    def display(self):
        if self._display is None:
            logger.debug("Initializing Display service")
            self._display = Display(
                xaddr=self._get_xaddr("display", "Display"), **self.common_args
            )
        return self._display

    # Analytics

    @service
    def analytics(self):
        if self._analytics is None:
            logger.debug("Initializing Analytics service")
            self._analytics = Analytics(
                xaddr=self._get_xaddr("analytics", "Analytics"), **self.common_args
            )
        return self._analytics

    @service
    def ruleengine(self):
        if self._ruleengine is None:
            logger.debug("Initializing RuleEngine service")
            self._ruleengine = RuleEngine(
                xaddr=self._get_xaddr("ruleengine", "Analytics"), **self.common_args
            )
        return self._ruleengine

    @service
    def analyticsdevice(self):
        if self._analyticsdevice is None:
            logger.debug("Initializing AnalyticsDevice service")
            self._analyticsdevice = AnalyticsDevice(
                xaddr=self._get_xaddr("analyticsdevice", "AnalyticsDevice"),
                **self.common_args,
            )
        return self._analyticsdevice

    # PACS

    @service
    def accesscontrol(self):
        if self._accesscontrol is None:
            logger.debug("Initializing AccessControl service")
            self._accesscontrol = AccessControl(
                xaddr=self._get_xaddr("accesscontrol", "AccessControl"),
                **self.common_args,
            )
        return self._accesscontrol

    @service
    def doorcontrol(self):
        if self._doorcontrol is None:
            logger.debug("Initializing DoorControl service")
            self._doorcontrol = DoorControl(
                xaddr=self._get_xaddr("doorcontrol", "DoorControl"), **self.common_args
            )
        return self._doorcontrol

    # AccessRules

    @service
    def accessrules(self):
        if self._accessrules is None:
            logger.debug("Initializing AccessRules service")
            self._accessrules = AccessRules(
                xaddr=self._get_xaddr("accessrules", "AccessRules"), **self.common_args
            )
        return self._accessrules

    # ActionEngine

    @service
    def actionengine(self):
        if self._actionengine is None:
            logger.debug("Initializing ActionEngine service")
            self._actionengine = ActionEngine(
                xaddr=self._get_xaddr("actionengine", "ActionEngine"),
                **self.common_args,
            )
        return self._actionengine

    # AppManagement

    @service
    def appmanagement(self):
        if self._appmanagement is None:
            logger.debug("Initializing AppManagement service")
            self._appmanagement = AppManagement(
                xaddr=self._get_xaddr("appmgmt", "AppManagement"),
                **self.common_args,
            )
        return self._appmanagement

    # AuthenticationBehavior

    @service
    def authenticationbehavior(self):
        if self._authenticationbehavior is None:
            logger.debug("Initializing AuthenticationBehavior service")
            self._authenticationbehavior = AuthenticationBehavior(
                xaddr=self._get_xaddr(
                    "authenticationbehavior", "AuthenticationBehavior"
                ),
                **self.common_args,
            )
        return self._authenticationbehavior

    # Credential

    @service
    def credential(self):
        if self._credential is None:
            logger.debug("Initializing Credential service")
            self._credential = Credential(
                xaddr=self._get_xaddr("credential", "Credential"),
                **self.common_args,
            )
        return self._credential

    # Recording

    @service
    def recording(self):
        if self._recording is None:
            logger.debug("Initializing Recording service")
            self._recording = Recording(
                xaddr=self._get_xaddr("recording", "Recording"),
                **self.common_args,
            )
        return self._recording

    # Replay

    @service
    def replay(self):
        if self._replay is None:
            logger.debug("Initializing Replay service")
            self._replay = Replay(
                xaddr=self._get_xaddr("replay", "Replay"),
                **self.common_args,
            )
        return self._replay

    # Provisioning

    @service
    def provisioning(self):
        if self._provisioning is None:
            logger.debug("Initializing Provisioning service")
            self._provisioning = Provisioning(
                xaddr=self._get_xaddr("provisioning", "Provisioning"),
                **self.common_args,
            )
        return self._provisioning

    # Receiver

    @service
    def receiver(self):
        if self._receiver is None:
            logger.debug("Initializing Receiver service")
            self._receiver = Receiver(
                xaddr=self._get_xaddr("receiver", "Receiver"),
                **self.common_args,
            )
        return self._receiver

    # Schedule

    @service
    def schedule(self):
        if self._schedule is None:
            logger.debug("Initializing Schedule service")
            self._schedule = Schedule(
                xaddr=self._get_xaddr("schedule", "Schedule"),
                **self.common_args,
            )
        return self._schedule

    # Search Recording

    @service
    def search(self):
        if self._search is None:
            logger.debug("Initializing Search service")
            self._search = Search(
                xaddr=self._get_xaddr("search", "Search"),
                **self.common_args,
            )
        return self._search

    # Thermal

    @service
    def thermal(self):
        if self._thermal is None:
            logger.debug("Initializing Thermal service")
            self._thermal = Thermal(
                xaddr=self._get_xaddr("thermal", "Thermal"),
                **self.common_args,
            )
        return self._thermal

    # Uplink

    @service
    def uplink(self):
        if self._uplink is None:
            logger.debug("Initializing Uplink service")
            self._uplink = Uplink(
                xaddr=self._get_xaddr("uplink", "Uplink"),
                **self.common_args,
            )
        return self._uplink

    # Security - AdvancedSecurity

    @service
    def security(self):
        if self._security is None:
            logger.debug("Initializing Security service")
            self._security = AdvancedSecurity(
                **self.common_args,
            )
        return self._security

    @service
    def jwt(self):
        if self._jwt is None:
            logger.debug("Initializing JWT service")
            self._jwt = JWT(**self.common_args)
        return self._jwt

    @service
    def keystore(self, xaddr):
        if self._keystore is None:
            logger.debug("Initializing Keystore service")
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._keystore = Keystore(xaddr=xaddr, **self.common_args)
        return self._keystore

    @service
    def tlsserver(self, xaddr):
        if self._tlsserver is None:
            logger.debug("Initializing TLSServer service")
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._tlsserver = TLSServer(xaddr=xaddr, **self.common_args)
        return self._tlsserver

    @service
    def dot1x(self, xaddr):
        if self._dot1x is None:
            logger.debug("Initializing Dot1X service")
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._dot1x = Dot1X(xaddr=xaddr, **self.common_args)
        return self._dot1x

    @service
    def authorizationserver(self, xaddr):
        if self._authorizationserver is None:
            logger.debug("Initializing AuthorizationServer service")
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._authorizationserver = AuthorizationServer(
                xaddr=xaddr, **self.common_args
            )
        return self._authorizationserver

    @service
    def mediasigning(self, xaddr):
        if self._mediasigning is None:
            logger.debug("Initializing MediaSigning service")
            xaddr = self._rewrite_xaddr_if_needed(xaddr)
            self._mediasigning = MediaSigning(xaddr=xaddr, **self.common_args)
        return self._mediasigning
