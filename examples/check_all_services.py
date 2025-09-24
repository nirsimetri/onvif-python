"""
Path: examples/check_all_services.py
Author: @kaburagisec
Created: September 17, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and retrieves a list
of all available services using the Core (Device Management) service.
"""

from onvif import ONVIFClient

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

try:
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
    services = client.devicemgmt().GetServices(IncludeCapability=True)
    print(services)
except Exception as e:
    print(e)
