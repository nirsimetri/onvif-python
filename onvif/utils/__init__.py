"""Utility functions and classes for ONVIF operations."""

from onvif.utils.discovery import ONVIFDiscovery
from onvif.utils.error_handlers import (
    ignore_unsupported,
    is_action_not_supported,
    safe_call,
)
from onvif.utils.exceptions import ONVIFOperationException
from onvif.utils.plugins import ONVIFParser, XMLCapturePlugin
from onvif.utils.service import ONVIFService
from onvif.utils.wsdl import ONVIFWSDL
from onvif.utils.zeep import ZeepPatcher

__all__ = [
    "ONVIFWSDL",
    "ONVIFOperationException",
    "ZeepPatcher",
    "XMLCapturePlugin",
    "ONVIFDiscovery",
    "ONVIFService",
    "ONVIFParser",
    "ignore_unsupported",
    "is_action_not_supported",
    "safe_call",
]
