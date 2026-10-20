"""
Path: examples/get_media_profiles.py
Author: @kaburagisec
Created: October 11, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and retrieves
the media profiles using the Media service.
"""

from onvif import ONVIFClient, ONVIFOperationException

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "password"

try:
    client = ONVIFClient(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)
    device = client.media()

    # print available media profiles
    print(device.GetProfiles())
except ONVIFOperationException as e:
    print(e)
