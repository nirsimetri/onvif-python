"""
Path: examples/set_irlamp.py
Author: @kaburagisec
Created: September 23, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and sets the IR lamp (Infra Red)
to ON, OFF, or AUTO mode using the Imaging service.
"""

from onvif import ONVIFClient, ONVIFOperationException

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "password"

try:
    client = ONVIFClient(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)
    media = client.media()
    profile = media.GetProfiles()[0]  # use first profile
    video_source_token = profile.VideoSourceConfiguration.SourceToken

    imaging = client.imaging()

    # Normal vendor implement IR (Infra Red) lamp control via Imaging service
    # Here we set it to ON, OFF or AUTO (if supported by the camera)
    imaging.SetImagingSettings(
        VideoSourceToken=video_source_token, ImagingSettings={"IrCutFilter": "ON"}
    )

    print(imaging.GetImagingSettings(VideoSourceToken=video_source_token))
except (ONVIFOperationException, KeyError) as e:
    print(e)
