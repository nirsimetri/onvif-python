# onvif/__init__.py

from .client import ONVIFClient
from .operator import ONVIFOperator, CacheMode
from .utils import ONVIFWSDL, ONVIFOperationException, ONVIFErrorHandler, ZeepPatcher

# CLI module is optional - import only if needed
try:
    from .cli import main as ONVIFCLI

    CLI_AVAILABLE = True
except ImportError:
    CLI_AVAILABLE = False

__all__ = [
    "ONVIFClient",
    "ONVIFOperator",
    "CacheMode",
    "ONVIFWSDL",
    "ONVIFOperationException",
    "ONVIFErrorHandler",
    "ZeepPatcher",
]

if CLI_AVAILABLE:
    __all__.append("ONVIFCLI")
