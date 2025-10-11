"""
Path: examples/get_imaging.py
Author: @kaburagisec
Created: October 11, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and retrieves its
imaging settings using the Imaging service from the first media profile.
"""

from onvif import ONVIFClient

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

try:
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
    profile = client.media().GetProfiles()[0]  # use the first profile
    imaging = client.imaging()

    print(
        imaging.GetImagingSettings(
            VideoSourceToken=profile.VideoSourceConfiguration.SourceToken
        )
    )
except Exception as e:
    print(e)
