"""
Path: examples/get_onvif_version.py
Author: @kaburagisec
Created: September 23, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and retrieves its
ONVIF version using the Device Management service.
"""

from onvif import ONVIFClient

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

try:
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
    device = client.devicemgmt()

    services = device.GetServices(IncludeCapability=False)
    for service in services:
        if (
            service["Namespace"] == "http://www.onvif.org/ver10/device/wsdl"
        ):  # ONVIF Version is from Device service
            print(service["Version"])
except Exception as e:
    print(e)
