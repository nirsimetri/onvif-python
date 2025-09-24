"""
Path: examples/get_onvif_version.py
Author: @kaburagisec
Created: September 23, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)
"""

from onvif import ONVIFClient

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

try:
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
    device = client.devicemgmt()


except Exception as e:
    print(e)
