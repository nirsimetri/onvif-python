"""
Path: examples/check_all_capabilities.py
Author: @kaburagisec
Created: September 18, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and retrieves its
capabilities using the Core (Device Management) service.
"""

from onvif import ONVIFClient, CacheMode

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

try:
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD, cache=CacheMode.NONE)
    capabilities = client.devicemgmt().GetCapabilities(Category="All")
    print(capabilities)
except Exception as e:
    print(e)
