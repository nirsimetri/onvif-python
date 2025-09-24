"""
Path: examples/open_stream_with_ptz.py
Author: @kaburagisec
Created: September 23, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device, retrieves the RTSP stream URI,
opens the video stream using OpenCV, and allows PTZ control via keyboard.
PTZ movement stops automatically when no key is pressed.
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
ptz = client.ptz()

profile = media.GetProfiles()[0]  # use the first profile
print("Profile Name:", profile.Name)

stream = media.GetStreamUri(
    ProfileToken=profile.token,
    StreamSetup={"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}},
)
print("Token:", profile.token)
print("Stream:\n", stream)

# Encode username/password for RTSP
username_enc = urllib.parse.quote(USERNAME)
password_enc = urllib.parse.quote(PASSWORD)
rtsp_url_with_auth = stream.Uri.replace(
    "rtsp://", f"rtsp://{username_enc}:{password_enc}@"
)

window_name = f"ONVIF Camera Stream with PTZ ({HOST}:{PORT}) - ({rtsp_url_with_auth})"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 800, 600)

print("Connecting to RTSP stream:", rtsp_url_with_auth)
cap = cv2.VideoCapture(rtsp_url_with_auth)
if not cap.isOpened():
    print("❌ Failed to open RTSP stream:", rtsp_url_with_auth)
    sys.exit(1)

print("✅ Streaming started.")
print("ℹ️ Use keys W/S/A/D to tilt/pan, Q/E to zoom in/out, ESC to quit.")

# PTZ control parameters
pan_speed = 0.5
tilt_speed = 0.5
zoom_speed = 0.5


def move(ptz, token, pan=0, tilt=0, zoom=0):
    velocity = {}
    if pan or tilt:
        velocity["PanTilt"] = {"x": pan, "y": tilt}
    if zoom:
        velocity["Zoom"] = {"x": zoom}
    ptz.ContinuousMove(ProfileToken=token, Velocity=velocity)


def stop(ptz, token):
    ptz.Stop(ProfileToken=token, PanTilt=True, Zoom=True)


last_key = None  # track last movement key

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Empty frame")
        break

    x, y, w, h = cv2.getWindowImageRect(window_name)
    frame_resized = cv2.resize(frame, (w, h)) if w > 0 and h > 0 else frame
    cv2.imshow(window_name, frame_resized)

    key = cv2.waitKey(10) & 0xFF
    movement_keys = {ord("w"), ord("s"), ord("a"), ord("d"), ord("q"), ord("e")}
    if key in movement_keys:
        last_key = key
        if key == ord("w"):  # tilt up
            move(ptz, profile.token, tilt=tilt_speed)
        elif key == ord("s"):  # tilt down
            move(ptz, profile.token, tilt=-tilt_speed)
        elif key == ord("a"):  # pan left
            move(ptz, profile.token, pan=-pan_speed)
        elif key == ord("d"):  # pan right
            move(ptz, profile.token, pan=pan_speed)
        elif key == ord("q"):  # zoom in
            move(ptz, profile.token, zoom=zoom_speed)
        elif key == ord("e"):  # zoom out
            move(ptz, profile.token, zoom=-zoom_speed)
    else:
        # If no movement key is pressed, stop PTZ
        if last_key is not None:
            stop(ptz, profile.token)
            last_key = None
        if key == 27:  # ESC -> quit
            break

cap.release()
cv2.destroyAllWindows()

# Ensure PTZ is stopped on exit
stop(ptz, profile.token)
