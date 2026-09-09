"""ONVIFClient: High-level ONVIF client for interacting with ONVIF-compliant devices."""

from __future__ import annotations

import logging
from functools import wraps
from urllib.parse import urlparse, urlunparse

from onvif.operator import CacheMode
from onvif.services import (
    JWT,
    PTZ,
    AccessControl,
    AccessRules,
    ActionEngine,
    AdvancedSecurity,
    Analytics,
    AnalyticsDevice,
    AppManagement,
    AuthenticationBehavior,
    AuthorizationServer,
    Credential,
    Device,
    DeviceIO,
    Display,
    DoorControl,
    Dot1X,
    Events,
    Imaging,
    Keystore,
    Media,
    Media2,
    MediaSigning,
    Notification,
    PausableSubscription,
    Provisioning,
    PullPoint,
    Receiver,
    Recording,
    Replay,
    RuleEngine,
    Schedule,
    Search,
    Subscription,
    Thermal,
    TLSServer,
    Uplink,
)
from onvif.utils import (
    ONVIFWSDL,
    ONVIFOperationException,
    XMLCapturePlugin,
    ZeepPatcher,
)

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
            logger.error("Service initialization failed in %s: %s", func.__name__, oe)
            raise
        except Exception as e:
            # Wrap any other exception in ONVIFOperationException
            logger.error("Service initialization failed in %s: %s", func.__name__, e)
            raise ONVIFOperationException(func.__name__, e) from e

    return wrapper


# pylint: disable=too-many-instance-attributes,too-many-locals,too-many-public-methods,too-many-statements
class ONVIFClient:
    """ONVIF Client for communicating with ONVIF-compliant devices.

    This is the main class for interacting with ONVIF devices. It provides access to
    all ONVIF services including Device Management, Media, PTZ, Events, Analytics, and more.

    The client automatically discovers available services on the device using GetServices
    or GetCapabilities, and provides lazy initialization for service endpoints.

    Attributes:
        services (list): List of available services from GetServices response
        capabilities (CompoundValue): Device capabilities from GetCapabilities response (fallback)
        xml_plugin (XMLCapturePlugin): XML capture plugin for debugging (if capture_xml=True)
        wsdl_dir (str | None): Custom WSDL directory path (if provided)
    """

    def __init__(
        self,
        host: str,
        port: int,
        username: str | None = None,
        password: str | None = None,
        http_digest: bool = False,  # will use WS-Usernametoken by default (recommended! trust me)
        timeout: int = 10,
        cache: CacheMode = CacheMode.ALL,
        use_https: bool = False,
        verify_ssl: bool = False,
        apply_patch: bool = True,
        capture_xml: bool = False,
        wsdl_dir: str | None = None,
        plugins: list | None = None,
    ):
        """Initialize the ONVIF client.

        Args:
            host (str): Device hostname or IP address
            port (int): Device port number
            username (str | None): ONVIF username
            password (str | None): ONVIF password
            http_digest (bool): Whether to use HTTP Digest or WS-Usernametoken for auth
            timeout (int): Request timeout in seconds
            cache (CacheMode): WSDL caching strategy
            use_https (bool): Use HTTPS instead of HTTP for secure communication
            verify_ssl (bool): Whether SSL certificates should be verified
            apply_patch (bool): Whether to apply ``xsd:any`` flattening patch
            capture_xml (bool): Whether to use XML capture plugin for debugging SOAP requests/responses
            wsdl_dir (str | None): Custom WSDL directory path for using external WSDL files instead of built-in ones
            plugins (list | None): List of enabled Zeep plugins
        """

        logger.info("Initializing ONVIF client for %s:%d", host, port)
        logger.debug(
            "Connection settings: HTTPS=%s, SSL_verify=%s, cache=%s, timeout=%ds",
            use_https,
            verify_ssl,
            cache.value,
            timeout,
        )

        # Apply or remove zeep patch based on user preference
        self._configure_patches(apply_patch)

        # Initialize XML capture plugin if requested
        # and merge user plugins with xml_plugin
        all_plugins = self._configure_plugins(
            capture_xml,
            plugins,
        )

        # Store custom WSDL directory if provided
        self.wsdl_dir: str | None = wsdl_dir
        if wsdl_dir:
            logger.debug("Using custom WSDL directory: %s", wsdl_dir)
            ONVIFWSDL.set_custom_wsdl_dir(wsdl_dir)

        # Pass to ONVIFOperator
        self.common_args = {
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "http_digest": http_digest,
            "timeout": timeout,
            "cache": cache,
            "use_https": use_https,
            "verify_ssl": verify_ssl,
            "apply_patch": apply_patch,
            "plugins": all_plugins if all_plugins else None,
        }

        # Device Management (Core) service is always available
        self._devicemgmt: Device | None = None
        self._devicemgmt = self.devicemgmt()

        # Try to retrieve device services and create namespace -> XAddr mapping
        self.services = None
        self._service_map = {}

        # Temporary variable to hold capabilities
        self.capabilities = None

        try:
            # Try GetServices first (preferred method)
            logger.debug("Attempting GetServices call for service discovery")
            self.services = self._devicemgmt.GetServices(IncludeCapability=False)
            logger.info("Found %d services via GetServices", len(self.services))

            for onvif_service in self.services:
                namespace = getattr(onvif_service, "Namespace", None)
                xaddr = getattr(onvif_service, "XAddr", None)

                if namespace and xaddr:
                    self._service_map[namespace] = xaddr
                    logger.debug("Mapped service: %s -> %s", namespace, xaddr)
        except Exception as e:  # pylint: disable=broad-except
            logger.warning("GetServices failed: %s", e)
            # Fallback to GetCapabilities if GetServices is not supported on device
            try:
                logger.debug("Falling back to GetCapabilities")
                self.capabilities = self._devicemgmt.GetCapabilities(Category="All")
                logger.info("Successfully retrieved device capabilities")
            except Exception as e2:  # pylint: disable=broad-except
                # If both fail, we'll use default URLs
                logger.error("Both GetServices and GetCapabilities failed: %s", e2)
                logger.warning("Using default URLs for services")

        # Lazy init for other services

        self._events: Events | None = None
        self._pullpoints: dict[str, PullPoint] = (
            {}
        )  # Dictionary for multiple PullPoint instances
        self._notification: Notification | None = None
        self._subscriptions: dict[str, Subscription] = (
            {}
        )  # Dictionary for multiple Subscription instances
        self._pausable_subscriptions: dict[str, PausableSubscription] = (
            {}
        )  # Dictionary for multiple PausableSubscription instances

        self._imaging: Imaging | None = None

        self._media: Media | None = None
        self._media2: Media2 | None = None

        self._ptz: PTZ | None = None

        self._deviceio: DeviceIO | None = None

        self._display: Display | None = None

        self._analytics: Analytics | None = None
        self._ruleengine: RuleEngine | None = None
        self._analyticsdevice: AnalyticsDevice | None = None

        self._accesscontrol: AccessControl | None = None
        self._doorcontrol: DoorControl | None = None

        self._accessrules: AccessRules | None = None

        self._actionengine: ActionEngine | None = None

        self._appmanagement: AppManagement | None = None

        self._authenticationbehavior: AuthenticationBehavior | None = None

        self._credential: Credential | None = None

        self._recording: Recording | None = None
        self._replay: Replay | None = None

        self._provisioning: Provisioning | None = None

        self._receiver: Receiver | None = None

        self._schedule: Schedule | None = None

        self._search: Search | None = None

        self._thermal: Thermal | None = None

        self._uplink: Uplink | None = None

        self._security: AdvancedSecurity | None = None
        self._jwt: JWT | None = None
        self._keystore: Keystore | None = None
        self._tlsserver: TLSServer | None = None
        self._dot1x: Dot1X | None = None
        self._authorizationserver: AuthorizationServer | None = None
        self._mediasigning: MediaSigning | None = None

    def _get_xaddr(
        self, service_name: str, service_path: str
    ):  # pylint: disable=too-many-branches
        """Resolve XAddr for ONVIF services using a comprehensive 3-tier discovery
        approach.

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
        logger.debug("Resolving XAddr for service: %s (%s)", service_name, service_path)

        # First try to get from GetServices mapping
        if self.services:
            logger.debug("Attempting resolution via GetServices")
            # Get the namespace for this service from WSDL_MAP
            try:
                # Try to get the service definition from WSDL_MAP
                # Most services use ver10, some use ver20
                wsdl_def = None
                wsdl_map = ONVIFWSDL.get_wsdl_map()
                service_map = wsdl_map.get(service_name)

                # Try ver10 first, then ver20
                if service_map is not None:
                    if "ver10" in service_map:
                        wsdl_def = service_map["ver10"]
                    elif "ver20" in service_map:
                        wsdl_def = service_map["ver20"]

                if wsdl_def:
                    namespace = wsdl_def["namespace"]
                    xaddr = self._service_map.get(namespace)

                    if xaddr:
                        # Rewrite host/port if needed
                        rewritten = self._rewrite_xaddr_if_needed(xaddr)
                        logger.debug(
                            "Resolved via GetServices: %s -> %s",
                            service_name,
                            rewritten,
                        )
                        return rewritten
            except (ValueError, TypeError, KeyError) as e:
                logger.debug(
                    "Service %s not found in GetServices mapping: %s", service_name, e
                )

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
                        "Resolved via GetCapabilities: %s -> %s",
                        service_name,
                        rewritten,
                    )
                    return rewritten
            except (AttributeError, ValueError, TypeError, KeyError) as e:
                logger.debug(
                    "Service %s not found in GetCapabilities mapping: %s",
                    service_name,
                    e,
                )

        # Fallback to default URL
        protocol = "https" if self.common_args["use_https"] else "http"
        default_url = f"{protocol}://{self.common_args['host']}:{self.common_args['port']}/onvif/{service_path}"
        logger.warning("Using default URL for %s: %s", service_name, default_url)
        return default_url

    def _rewrite_xaddr_if_needed(self, xaddr: str):
        """Rewrite XAddr to use client's host/port if different from device's."""
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
                logger.debug("Rewritten XAddr: %s -> %s", xaddr, rewritten)
                return rewritten

            logger.debug("XAddr unchanged: %s", xaddr)
            return xaddr
        except (ValueError, TypeError, KeyError) as e:
            logger.warning("Failed to parse XAddr %s, returning as-is: %s", xaddr, e)
            return xaddr

    def _configure_patches(self, apply_patch: bool) -> None:
        """Configure Zeep patches."""
        if apply_patch:
            logger.debug("Applying ZeepPatcher")
            ZeepPatcher.apply_patch()
        else:
            logger.debug("Removing ZeepPatcher")
            ZeepPatcher.remove_patch()

    def _configure_plugins(
        self,
        capture_xml: bool,
        plugins: list | None,
    ) -> list:
        """Configure client plugins."""
        all_plugins = list(plugins) if plugins else []

        if plugins:
            logger.debug("Adding %d user-provided plugins", len(plugins))

        self.xml_plugin = None

        if capture_xml:
            logger.debug("Enabling XML capture plugin")
            self.xml_plugin = XMLCapturePlugin()
            all_plugins.append(self.xml_plugin)

        return all_plugins

    # Core (Device Management)

    @service
    def devicemgmt(self):
        """Access the Device Management service."""
        if self._devicemgmt is None:
            logger.debug("Initializing Device Management service")
            self._devicemgmt = Device(**self.common_args)
        return self._devicemgmt

    # Core (Events)

    @service
    def events(self):
        """Access the Events service."""
        if self._events is None:
            logger.debug("Initializing Events service")
            self._events = Events(
                xaddr=self._get_xaddr("events", "Events"), **self.common_args
            )
        return self._events

    @service
    def pullpoint(self, SubscriptionRef):  # pylint: disable=invalid-name
        """Access the PullPoint service."""
        logger.debug("Initializing PullPoint service")
        xaddr = None
        addr_obj = SubscriptionRef["SubscriptionReference"]["Address"]
        if isinstance(addr_obj, dict) and "_value_1" in addr_obj:
            xaddr = addr_obj["_value_1"]
        elif hasattr(addr_obj, "_value_1"):
            xaddr = addr_obj._value_1  # pylint: disable=protected-access

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
        """Access the Notification service."""
        if self._notification is None:
            logger.debug("Initializing Notification service")
            self._notification = Notification(
                xaddr=self._get_xaddr("notification", "Events"), **self.common_args
            )
        return self._notification

    @service
    def subscription(self, SubscriptionRef):  # pylint: disable=invalid-name
        """Access the Subscription service."""
        logger.debug("Initializing Subscription service")
        xaddr = None
        addr_obj = SubscriptionRef["SubscriptionReference"]["Address"]
        if isinstance(addr_obj, dict) and "_value_1" in addr_obj:
            xaddr = addr_obj["_value_1"]
        elif hasattr(addr_obj, "_value_1"):
            xaddr = addr_obj._value_1  # pylint: disable=protected-access

        xaddr = self._rewrite_xaddr_if_needed(xaddr)

        if not xaddr:
            raise RuntimeError(
                "SubscriptionReference.Address missing in subscription response"
            )

        if xaddr not in self._subscriptions:
            self._subscriptions[xaddr] = Subscription(xaddr=xaddr, **self.common_args)

        return self._subscriptions[xaddr]

    @service
    def pausable_subscription(self, SubscriptionRef):  # pylint: disable=invalid-name
        """Access the PausableSubscription service."""
        logger.debug("Initializing PausableSubscription service")
        xaddr = None
        addr_obj = SubscriptionRef["SubscriptionReference"]["Address"]
        if isinstance(addr_obj, dict) and "_value_1" in addr_obj:
            xaddr = addr_obj["_value_1"]
        elif hasattr(addr_obj, "_value_1"):
            xaddr = addr_obj._value_1  # pylint: disable=protected-access

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
        """Access the Imaging service."""
        if self._imaging is None:
            logger.debug("Initializing Imaging service")
            self._imaging = Imaging(
                xaddr=self._get_xaddr("imaging", "Imaging"), **self.common_args
            )
        return self._imaging

    # Media

    @service
    def media(self):
        """Access the Media service."""
        if self._media is None:
            logger.debug("Initializing Media service")
            self._media = Media(
                xaddr=self._get_xaddr("media", "Media"), **self.common_args
            )
        return self._media

    @service
    def media2(self):
        """Access the Media2 service."""
        if self._media2 is None:
            logger.debug("Initializing Media2 service")
            self._media2 = Media2(
                xaddr=self._get_xaddr("media2", "Media2"), **self.common_args
            )
        return self._media2

    # PTZ

    @service
    def ptz(self):
        """Access the PTZ service."""
        if self._ptz is None:
            logger.debug("Initializing PTZ service")
            self._ptz = PTZ(xaddr=self._get_xaddr("ptz", "PTZ"), **self.common_args)
        return self._ptz

    # DeviceIO

    @service
    def deviceio(self):
        """Access the DeviceIO service."""
        if self._deviceio is None:
            logger.debug("Initializing DeviceIO service")
            self._deviceio = DeviceIO(
                xaddr=self._get_xaddr("deviceio", "DeviceIO"), **self.common_args
            )
        return self._deviceio

    # Display

    @service
    def display(self):
        """Access the Display service."""
        if self._display is None:
            logger.debug("Initializing Display service")
            self._display = Display(
                xaddr=self._get_xaddr("display", "Display"), **self.common_args
            )
        return self._display

    # Analytics

    @service
    def analytics(self):
        """Access the Analytics service."""
        if self._analytics is None:
            logger.debug("Initializing Analytics service")
            self._analytics = Analytics(
                xaddr=self._get_xaddr("analytics", "Analytics"), **self.common_args
            )
        return self._analytics

    @service
    def ruleengine(self):
        """Access the RuleEngine service."""
        if self._ruleengine is None:
            logger.debug("Initializing RuleEngine service")
            self._ruleengine = RuleEngine(
                xaddr=self._get_xaddr("ruleengine", "Analytics"), **self.common_args
            )
        return self._ruleengine

    @service
    def analyticsdevice(self):
        """Access the AnalyticsDevice service."""
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
        """Access the AccessControl service."""
        if self._accesscontrol is None:
            logger.debug("Initializing AccessControl service")
            self._accesscontrol = AccessControl(
                xaddr=self._get_xaddr("accesscontrol", "AccessControl"),
                **self.common_args,
            )
        return self._accesscontrol

    @service
    def doorcontrol(self):
        """Access the DoorControl service."""
        if self._doorcontrol is None:
            logger.debug("Initializing DoorControl service")
            self._doorcontrol = DoorControl(
                xaddr=self._get_xaddr("doorcontrol", "DoorControl"), **self.common_args
            )
        return self._doorcontrol

    # AccessRules

    @service
    def accessrules(self):
        """Access the AccessRules service."""
        if self._accessrules is None:
            logger.debug("Initializing AccessRules service")
            self._accessrules = AccessRules(
                xaddr=self._get_xaddr("accessrules", "AccessRules"), **self.common_args
            )
        return self._accessrules

    # ActionEngine

    @service
    def actionengine(self):
        """Access the ActionEngine service."""
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
        """Access the AppManagement service."""
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
        """Access the AuthenticationBehavior service."""
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
        """Access the Credential service."""
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
        """Access the Recording service."""
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
        """Access the Replay service."""
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
        """Access the Provisioning service."""
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
        """Access the Receiver service."""
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
        """Access the Schedule service."""
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
        """Access the Search service."""
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
        """Access the Thermal service."""
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
        """Access the Uplink service."""
        if self._uplink is None:
            logger.debug("Initializing Uplink service")
            self._uplink = Uplink(
                xaddr=self._get_xaddr("uplink", "Uplink"),
                **self.common_args,
            )
        return self._uplink

    # Security / AdvancedSecurity

    @service
    def security(self):
        """Access the AdvancedSecurity service."""
        if self._security is None:
            logger.debug("Initializing Security service")
            self._security = AdvancedSecurity(
                xaddr=self._get_xaddr("advancedsecurity", "Security"),
                **self.common_args,
            )
        return self._security

    @service
    def jwt(self):
        """Access the JWT service."""
        if self._jwt is None:
            logger.debug("Initializing JWT service")
            self._jwt = JWT(
                xaddr=self._get_xaddr("jwt", "Security"), **self.common_args
            )
        return self._jwt

    @service
    def keystore(self):
        """Access the Keystore service."""
        if self._keystore is None:
            logger.debug("Initializing Keystore service")
            self._keystore = Keystore(
                xaddr=self._get_xaddr("keystore", "Security"), **self.common_args
            )
        return self._keystore

    @service
    def tlsserver(self):
        """Access the TLSServer service."""
        if self._tlsserver is None:
            logger.debug("Initializing TLSServer service")
            self._tlsserver = TLSServer(
                xaddr=self._get_xaddr("tlsserver", "Security"), **self.common_args
            )
        return self._tlsserver

    @service
    def dot1x(self):
        """Access the Dot1X service."""
        if self._dot1x is None:
            logger.debug("Initializing Dot1X service")
            self._dot1x = Dot1X(
                xaddr=self._get_xaddr("dot1x", "Security"), **self.common_args
            )
        return self._dot1x

    @service
    def authorizationserver(self):
        """Access the AuthorizationServer service."""
        if self._authorizationserver is None:
            logger.debug("Initializing AuthorizationServer service")
            self._authorizationserver = AuthorizationServer(
                xaddr=self._get_xaddr("authorizationserver", "Security"),
                **self.common_args,
            )
        return self._authorizationserver

    @service
    def mediasigning(self):
        """Access the MediaSigning service."""
        if self._mediasigning is None:
            logger.debug("Initializing MediaSigning service")
            self._mediasigning = MediaSigning(
                xaddr=self._get_xaddr("mediasigning", "Security"), **self.common_args
            )
        return self._mediasigning
