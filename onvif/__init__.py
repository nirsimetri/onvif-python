"""ONVIF Python."""

from onvif.cli import main as ONVIFCLI
from onvif.client import ONVIFClient
from onvif.operator import CacheMode
from onvif.utils import (
    ONVIFWSDL,
    ONVIFDiscovery,
    ONVIFOperationException,
    ONVIFParser,
    ZeepPatcher,
    ignore_unsupported,
    is_action_not_supported,
    safe_call,
)

__all__ = [
    "ONVIFClient",
    "CacheMode",
    "ONVIFWSDL",
    "ONVIFOperationException",
    "ZeepPatcher",
    "ONVIFCLI",
    "ONVIFDiscovery",
    "ONVIFParser",
    "ignore_unsupported",
    "is_action_not_supported",
    "safe_call",
]
