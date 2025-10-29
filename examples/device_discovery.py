"""
Path: examples/device_discovery.py
Author: @kaburagisec
Created: October 24, 2025

This example demonstrates how to discover ONVIF-compatible devices
on the local network using ONVIFDiscovery class.

Applied for (>= v0.1.6 patch)
"""

import json
from onvif import ONVIFDiscovery

try:
    discovery = ONVIFDiscovery(timeout=5)
    devices = discovery.discover()
    print(json.dumps(devices, indent=2))
except Exception as e:
    print(e)
