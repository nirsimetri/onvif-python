"""
Path: examples/set_irlamp.py
Author: @kaburagisec
Created: September 23, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and sets the IR lamp (Infra Red)
to ON, OFF, or AUTO mode using the Imaging service.
"""

from onvif import ONVIFClient

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

try:
    # Normal vendor implement IR (Infra Red) lamp control via Imaging service
    # Here we set it to ON, OFF or AUTO (if supported by the camera)
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
    media = client.media()
    profile = media.GetProfiles()[0]
    video_source_token = profile.VideoSourceConfiguration.SourceToken

    imaging = client.imaging()
    imaging.SetImagingSettings(
        VideoSourceToken=video_source_token, ImagingSettings={"IrCutFilter": "ON"}
    )

    print(imaging.GetImagingSettings(VideoSourceToken=video_source_token))
except Exception as e:
    print(e)
