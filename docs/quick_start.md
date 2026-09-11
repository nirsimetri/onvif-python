Below are simple examples to help you get started with the ONVIF Python library. These demonstrate how to discover and connect to ONVIF-compliant devices and retrieve basic device information.

!!! tip "For beginners"
    If you're new to ONVIF and want to learn more, we highly recommend taking the official free online course provided by ONVIF at [Introduction to ONVIF Course](https://www.onvif.org/about/introduction-to-onvif-course). Please note that we are not endorsed or sponsored by ONVIF, see [Legal Notice](legal/legal_notice.md) for details.

### Discover ONVIF Devices (Optional)

Use [`ONVIFDiscovery`](api/cores/onvif_discovery.md) (applied at [`>=v0.1.6`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.6)) to automatically find ONVIF devices on your local network:

```python
from onvif import ONVIFDiscovery

# Create discovery instance
discovery = ONVIFDiscovery(timeout=5)

# or with a custom interface
discovery = ONVIFDiscovery(timeout=5, interface="192.168.1.69")

# Discover devices
devices = discovery.discover()

# Or with
# Discover with search filter by types or scopes
# (case-insensitive substring match)
devices = discovery.discover(search="Profile/Streaming")

# Display discovered devices
for device in devices:
    print(f"Found device at {device['host']}:{device['port']}")
    print(f"  Scopes: {device.get('scopes', [])}")
    print(f"  XAddrs: {device['xaddrs']}")
```

### Initialize the ONVIFClient

Create an instance of [`ONVIFClient`](api/cores/onvif_client.md) by providing your device's IP address, port, username, and password:

```python
from onvif import ONVIFClient

# Basic connection
client = ONVIFClient("192.168.1.17", 8000, "admin", "admin123")

# With custom WSDL directory (optional)
client = ONVIFClient(
    "192.168.1.17", 8000, "admin", "admin123",
    wsdl_dir="/path/to/custom/wsdl"  # Use custom WSDL files in this path
)
```

### Create Service Instance

[`ONVIFClient`](api/cores/onvif_client.md) provides several main services that can be accessed via the following methods:

- `client.devicemgmt()` — Device Management
- `client.events()` — Events
- `client.imaging()` — Imaging
- `client.media()` — Media
- `client.ptz()` — PTZ (Pan-Tilt-Zoom)
- `client.analytics()` — Analytics

and so on, check [`ONVIFClient`](api/cores/onvif_client.md) for more details

Example usage:
```python
device = client.devicemgmt()      # Device Management (Core)
media = client.media()            # Media
```

### Get Device Information

Retrieve basic information about the device, such as manufacturer, model, firmware version, and serial number using [`devicemgmt()`](api/services/device.md) service:

```python
info = device.GetDeviceInformation()
print(info)
# Example output:
# {'Manufacturer': '..', 'Model': '..', 'FirmwareVersion': '..', 'SerialNumber': '..'}
```

### Get RTSP URL

Retrieve the RTSP stream URL for live video streaming from the device using [`media()`](api/services/media.md) service:

```python
profile = media.GetProfiles()[0]  # use the first profile
stream = media.GetStreamUri(
    ProfileToken=profile.token, 
	StreamSetup={"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}}
)
print(stream)
# Example output:
# {'Uri': 'rtsp://192.168.1.17:8554/Streaming/Channels/101', ...}
```

Explore more advanced usage and service-specific operations in the [`examples/`](https://github.com/nirsimetri/onvif-python/tree/main/examples) folder.