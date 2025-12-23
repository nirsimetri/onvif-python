"""
Path: examples/check_device.py
Author: @kaburagisec
Created: September 17, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and retrieves basic
information such as device details and scopes using the Core (Device Management) service.
And using to_dict() (>= v0.2.8 patch) function to convert the response to a dictionary.
"""

import json
from onvif import ONVIFClient

HOST = "192.168.1.3"
PORT = 8000
USERNAME = "admin"
PASSWORD = "admin123"

try:
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
    device = client.devicemgmt()

    # print device information
    print(json.dumps(device.GetDeviceInformation().to_dict(), indent=4))

    # print device scopes
    print(json.dumps(device.GetScopes().to_dict(), indent=4))
except Exception as e:
    print(e)
