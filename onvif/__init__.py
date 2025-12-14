# onvif/__init__.py

__version__ = "0.2.7"

from .client import ONVIFClient
from .operator import CacheMode
from .utils import (
    ONVIFWSDL,
    ONVIFOperationException,
    ONVIFErrorHandler,
    ZeepPatcher,
    ONVIFDiscovery,
    ONVIFParser,
)
from .cli import main as ONVIFCLI

__all__ = [
    "ONVIFClient",
    "CacheMode",
    "ONVIFWSDL",
    "ONVIFOperationException",
    "ONVIFErrorHandler",
    "ZeepPatcher",
    "ONVIFCLI",
    "ONVIFDiscovery",
    "ONVIFParser",
    "__version__",
]
