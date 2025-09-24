"""
Path: examples/open_stream.py
Author: @kaburagisec
Created: September 18, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device, retrieves the RTSP stream URI,
and opens the video stream using OpenCV.
"""

import cv2
import sys
import urllib.parse

from onvif import ONVIFClient

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
media = client.media()

profile = media.GetProfiles()[0]  # use the first profile
print("Profile Name:", profile.Name)

stream = media.GetStreamUri(
    ProfileToken=profile.token,
    StreamSetup={"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}},
)
print("Token:", profile.token)
print("Stream:\n", stream)

# Encode username and password for RTSP URL
username_enc = urllib.parse.quote(USERNAME)
password_enc = urllib.parse.quote(PASSWORD)

rtsp_url = stream.Uri
rtsp_url_with_auth = rtsp_url.replace(
    "rtsp://", f"rtsp://{username_enc}:{password_enc}@"
)

window_name = f"ONVIF Camera Stream ({HOST}:{PORT}) - ({rtsp_url_with_auth})"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 800, 600)

print("Connecting to RTSP stream:", rtsp_url_with_auth)
cap = cv2.VideoCapture(rtsp_url_with_auth)
if not cap.isOpened():
    print("❌ Failed to open RTSP stream:", rtsp_url_with_auth)
    sys.exit(1)

print("✅ Streaming started.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Empty frame")
        break

    # Get current window size
    x, y, w, h = cv2.getWindowImageRect(window_name)
    # Resize frame to fit window
    if w > 0 and h > 0:
        frame_resized = cv2.resize(frame, (w, h))
    else:
        frame_resized = frame

    cv2.imshow(window_name, frame_resized)

    key = cv2.waitKey(10) & 0xFF

    if key == 27:  # ESC -> quit
        break

cap.release()
cv2.destroyAllWindows()
