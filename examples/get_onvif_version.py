"""
Path: examples/get_onvif_version.py
Author: @kaburagisec
Created: September 23, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compatible device and retrieves
the ONVIF versions supported by the camera.
"""

from onvif import ONVIFClient, ONVIFOperationException

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

try:
    client = ONVIFClient(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)
    device = client.devicemgmt()

    supported_versions = device.GetCapabilities(Category="All")["Device"]["System"][
        "SupportedVersions"
    ]
    print("Supported ONVIF Versions:")
    print(
        " ".join(f"[{version.Major}.{version.Minor}]" for version in supported_versions)
    )
except (ONVIFOperationException, KeyError, AttributeError) as e:
    print(e)
