"""
Path: examples/check_ptz.py
Author: @kaburagisec
Created: September 17, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script checks basic PTZ functionality of an ONVIF-compliant device.
"""

from time import sleep

from onvif import ONVIFClient, ONVIFOperationException

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "password"

try:
    client = ONVIFClient(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)
    media = client.media()
    profile = media.GetProfiles()[0]  # use first profile
    ptz = client.ptz()

    ptz.ContinuousMove(
        ProfileToken=profile.token,
        Velocity={"PanTilt": {"x": 0.1, "y": 0}},  # pan right
    )
    sleep(2)
    ptz.ContinuousMove(
        ProfileToken=profile.token,
        Velocity={"PanTilt": {"x": -0.1, "y": 0}},  # pan left
    )
    sleep(2.5)
    ptz.Stop(ProfileToken=profile.token)
except (ONVIFOperationException, KeyError) as e:
    print(e)
