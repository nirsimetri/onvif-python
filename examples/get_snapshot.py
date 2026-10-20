"""
Path: examples/get_snapshot.py
Author: @kaburagisec
Created: September 18, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and retrieves
the snapshot URI using the Media service.
"""

from onvif import ONVIFClient, ONVIFOperationException

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "password"

try:
    client = ONVIFClient(host=HOST, port=PORT, username=USERNAME, password=PASSWORD)
    media = client.media()

    profile = media.GetProfiles()[0]  # use the first profile
    print("Profile Name:", profile.Name)

    snapshot_uri = media.GetSnapshotUri(ProfileToken=profile.token)
    print("Snapshot URI:", snapshot_uri.Uri)
except (ONVIFOperationException, KeyError) as e:
    print(e)
