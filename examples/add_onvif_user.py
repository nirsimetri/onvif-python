"""
Path: examples/add_onvif_user.py
Author: @kaburagisec
Created: September 18, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and adds
a new user using the Core (Device Management) service.
"""

from onvif import ONVIFClient, ONVIFOperationException

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "password"

try:
    client = ONVIFClient(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)
    device = client.devicemgmt()
    device.CreateUsers(
        User=[{"Username": "newuser", "Password": "newpassword", "UserLevel": "User"}]
    )

    # print current users to verify addition
    print(device.GetUsers())
except ONVIFOperationException as e:
    print(e)
