With <a href="https://pepy.tech/projects/onvif-python"><img src="https://img.shields.io/pepy/dt/onvif-python?label=Total Downloads&color=red&style=plastic" alt="Total Downloads" style="vertical-align: -3.5px;"></a>, the `onvif-python` library is already being used by several well-known open-source projects, including:

## Viseron

[Viseron](https://viseron.netlify.app/) is an open-source self-hosted, local only NVR and AI Computer Vision software with support for ONVIF cameras.

<img src="https://viseron.netlify.app/img/ui/cameras/main.png" alt="Viseron" style="width: 100%; max-width: 900px;">

Viseron uses `onvif-python` as the underlying ONVIF client library for its ONVIF component. The integration currently covers the **Device**, **Media**, **Imaging**, and **PTZ** services, including device configuration, media profiles and stream URIs, imaging settings, and PTZ control.

ONVIF cameras can be configured through Viseron's dashboard, while PTZ cameras can also be controlled from the Live View interface.

For more information, see the [Viseron ONVIF component](https://viseron.netlify.app/components-explorer/components/onvif).

## pwneye

[pwneye](https://github.com/Hackerest/pwneye) is an ONVIF and RTSP camera security testing companion focused on discovering, enumerating, and interacting with real-world security cameras.

<video controls width="100%" height="40px">
  <source src="https://github.com/user-attachments/assets/6913632b-326d-455e-aa0d-be6bf9b3e66c" type="video/mp4">
  Your browser does not support the video tag.
</video>

It uses `onvif-python` for its ONVIF functionality, including WS-Discovery, authentication, device metadata, media profile and stream URI enumeration, PTZ control, device actions, and an interactive ONVIF shell.

The project also combines ONVIF capabilities with RTSP discovery, stream validation, recording, snapshots, and vendor-aware RTSP analysis.

For more information, see the [pwneye repository](https://github.com/Hackerest/pwneye).
