# onvif/operator.py

import os
import warnings
import requests
import urllib3

from enum import Enum
from zeep import Settings, Transport, Client, CachingClient
from zeep.cache import SqliteCache
from zeep.exceptions import Fault
from zeep.wsse.username import UsernameToken

from .utils import ONVIFOperationException, ZeepPatcher


class CacheMode(Enum):
    """WSDL caching strategies for ONVIF client performance optimization.

    Different caching modes provide trade-offs between performance, memory usage,
    and disk storage. Choose based on your application's requirements.

    Attributes:
        ALL: Maximum performance with both memory and disk caching
        DB: Disk-only caching for persistent storage
        MEM: Memory-only caching for temporary sessions
        NONE: No caching, always fetch fresh WSDLs
    """

    ALL = "all"  # CachingClient + SqliteCache →
    # (+) Fast startup (WSDL/schema cached in memory + disk), great for multi-device and long-running apps
    # (-) More complex, extra overhead on both disk and memory
    # Use case: Production servers with many cameras, need stability & bandwidth savings

    DB = "db"  # Client + SqliteCache →
    # (+) Persistent disk cache, saves bandwidth (WSDL/schema not fetched every time)
    # (-) Still parses full WSDL into memory at each startup
    # Use case: Batch jobs / CLI tools, or low-resource environments needing long-term cache

    MEM = "mem"  # CachingClient only →
    # (+) Lightweight compared to ALL, in-memory cache only, fast during runtime
    # (-) Cache lost on restart, WSDL will be fetched again after each restart
    # Use case: Short-lived scripts, demos, quick debugging, no need for disk persistence

    NONE = "none"  # Client only →
    # (+) Simplest, no caching at all
    # (-) Slow (always fetches & parses WSDL), high bandwidth usage
    # Use case: Pure debugging, small integration testing without performance concerns


class ONVIFOperator:
    """Low-level ONVIF service operator using Zeep SOAP client.

    This class handles the actual SOAP communication with ONVIF devices. It manages
    WSDL loading, service binding, authentication, caching, and error handling.

    ONVIFOperator is typically used internally by service classes (Device, Media, PTZ, etc.)
    and is not meant to be instantiated directly by end users. Use ONVIFClient instead.

    Attributes:
        wsdl_path (str): Path to the WSDL file
        host (str): Device hostname or IP address
        port (int): Device port number
        username (str): ONVIF username
        password (str): ONVIF password
        timeout (int): Request timeout in seconds
        apply_patch (bool): Whether to apply xsd:any flattening patch
        address (str): Service endpoint URL (XAddr)
        client: Zeep SOAP client instance
        service: Zeep service proxy for making SOAP calls
    """

    def __init__(
        self,
        wsdl_path: str,
        host: str,
        port: int,
        username: str = None,
        password: str = None,
        timeout: int = 10,
        binding: str = None,
        service_path: str = None,
        xaddr: str = None,
        cache: CacheMode = CacheMode.ALL,  # all | db | mem | none
        cache_path: str = None,
        use_https: bool = False,
        verify_ssl: bool = True,
        apply_patch: bool = True,
        plugins: list = None,
    ):
        self.wsdl_path = wsdl_path
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.apply_patch = apply_patch

        if xaddr:
            self.address = xaddr
        else:
            protocol = "https" if use_https else "http"
            path = service_path or "device_service"  # default fallback
            self.address = f"{protocol}://{host}:{port}/onvif/{path}"

        # Session reuse with retry strategy
        session = requests.Session()
        session.verify = verify_ssl

        # Format SSL warnings to be more concise when verify_ssl is False
        if not verify_ssl:
            warnings.simplefilter("once", urllib3.exceptions.InsecureRequestWarning)

        transport_kwargs = {"session": session, "timeout": timeout}

        if cache in (CacheMode.DB, CacheMode.ALL):
            if cache_path is None:
                user_cache_dir = os.path.expanduser("~/.onvif-python")
                os.makedirs(user_cache_dir, exist_ok=True)
                cache_path = os.path.join(user_cache_dir, "onvif_zeep_cache.sqlite")

            transport_kwargs["cache"] = SqliteCache(path=cache_path)

        transport = Transport(**transport_kwargs)

        # zeep settings
        settings = Settings(strict=False, xml_huge_tree=True)
        wsse = (
            UsernameToken(username, password, use_digest=True)
            if username and password
            else None
        )

        if cache == CacheMode.ALL:
            ClientType = CachingClient
        elif cache == CacheMode.MEM:
            ClientType = CachingClient
        elif cache == CacheMode.DB:
            ClientType = Client
        elif cache == CacheMode.NONE:
            ClientType = Client
        else:
            raise ValueError(f"Unknown cache option: {cache}")

        self.client = ClientType(
            wsdl=self.wsdl_path,
            transport=transport,
            settings=settings,
            wsse=wsse,
            plugins=plugins,
        )

        if not binding:
            raise ValueError("Bindings must be set according to the WSDL service")

        self.service = self.client.create_service(binding, self.address)
        # logging.debug(f"ONVIFOperator initialized {binding} at {self.address}")

    def call(self, method: str, *args, **kwargs):
        """Call an ONVIF service operation.

        This method invokes a SOAP operation on the ONVIF device service and handles
        errors gracefully. It automatically flattens xsd:any fields in the response
        when apply_patch is enabled.

        Args:
            method: Name of the ONVIF operation to call (e.g., "GetDeviceInformation")
            *args: Positional arguments to pass to the operation
            **kwargs: Keyword arguments to pass to the operation

        Returns:
            The operation result, with xsd:any fields flattened if apply_patch=True

        Raises:
            ONVIFOperationException: If the operation fails (wraps original exception)
        """
        try:
            func = getattr(self.service, method)
        except AttributeError as e:
            raise ONVIFOperationException(operation=method, original_exception=e)

        try:
            result = func(*args, **kwargs)
            # Post-process to flatten xsd:any fields if enabled (> v0.0.4 patch)
            if self.apply_patch:
                return ZeepPatcher.flatten_xsd_any_fields(result)
            return result
        except Fault as e:
            # logging.error(f"SOAP Fault in {method}: {e}")
            raise ONVIFOperationException(operation=method, original_exception=e)
        except Exception as e:
            # logging.error(f"ONVIF call error in {method}: {e}")
            raise ONVIFOperationException(operation=method, original_exception=e)
