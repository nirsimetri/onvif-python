!!! warning
    Before performing any operations on an ONVIF device, it is highly recommended to discover which services are available and supported by the device. This library automatically performs comprehensive service discovery during initialization using a robust fallback mechanism.

!!! tip
    The library handles service discovery automatically with intelligent fallback. You typically don't need to call discovery methods manually unless you need detailed capability information or want to refresh the service list after device configuration changes.

## Why discover device services?

- **Device Diversity:** Not all ONVIF devices support every service. Available services may vary by manufacturer, model, firmware, or configuration.
- **Error Prevention:** Attempting to use unsupported services can result in failed requests, exceptions, or undefined behavior.
- **Dynamic Feature Detection:** Devices may enable or disable services over time (e.g., after firmware updates or configuration changes).
- **Optimized Integration:** By checking available services, your application can adapt its workflow and UI to match the device's actual features.

## How service discovery works in this library

The `ONVIFClient` uses a **3-tier discovery approach** to maximize device compatibility:

1. **`GetServices` (Preferred)** - Tries `GetServices` first for detailed service information
2. **`GetCapabilities` (Fallback)** - Falls back to `GetCapabilities` if `GetServices` is not supported
3. **Default URLs (Final Fallback)** - Uses standard ONVIF URLs as last resort

```python
from onvif import ONVIFClient

client = ONVIFClient("192.168.1.17", 8000, "admin", "admin123")

# Check what discovery method was used
if client.services:
    print("Service discovery: GetServices (preferred)")
    print("Discovered services:", len(client.services))
    print("Service map:", client._service_map)
elif client.capabilities:
    print("Service discovery: GetCapabilities (fallback)")
    print("Available capabilities:", client.capabilities)
else:
    print("Service discovery: Using default URLs")
```

## Why this approach?

- `GetServices` provides the most accurate and detailed service information, but it's **optional** in the ONVIF specification
- `GetCapabilities` is **mandatory** for all ONVIF-compliant devices, ensuring broader compatibility
- **Default URLs** guarantee basic connectivity even with non-compliant devices

