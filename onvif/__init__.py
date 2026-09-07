"""onvif-python: A Python library for interacting with ONVIF-compliant devices."""

from typing import Final

__version__: Final[str] = "0.2.11"
__repository__: Final[str] = "https://github.com/nirsimetri/onvif-python"

from .cli import main as ONVIFCLI
from .client import ONVIFClient
from .operator import CacheMode
from .utils import (
    ONVIFWSDL,
    ONVIFDiscovery,
    ONVIFErrorHandler,
    ONVIFOperationException,
    ONVIFParser,
    ZeepPatcher,
)

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
    "__repository__",
]
