"""
Path: examples/set_imaging.py
Author: @kaburagisec
Created: September 07, 2026
Tested devices: UNIVIEW Uho-S2E (https://www.uniarch.cn//Products/Wireless_Series/Basic_Series/Basic_Series/Uho-S2E-M4/)

This script connects to an ONVIF-compliant device and sets the Imaging settings
with defined parameters.
"""

from onvif import ONVIFClient

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

try:
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
    media = client.media()
    profile = media.GetProfiles()[0]  # use first profile
    video_source_token = profile.VideoSourceConfiguration.SourceToken

    imaging = client.imaging()
    imaging.SetImagingSettings(
        VideoSourceToken=video_source_token,
        ImagingSettings={
            "Brightness": 50.0,
            "Contrast": 50.0,
            "WideDynamicRange": {"Mode": "ON", "Level": 50.0},
        },
    )

    print(imaging.GetImagingSettings(VideoSourceToken=video_source_token))
except Exception as e:  # pylint: disable=broad-exception-caught
    print(e)
