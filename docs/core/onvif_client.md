The [`ONVIFClient`](../api/core/onvif_client.md) class provides various configuration options to customize the connection behavior, caching strategy, security settings, and debugging capabilities. Below is a detailed description of all available parameters:


### Basic Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `host` | `str` | ✅ Yes | *required* | IP address or hostname of the ONVIF device (e.g., `"192.168.1.17"` or `"cctv.example.com"`) |
| `port` | `int` | ✅ Yes | *required* | Port number for ONVIF service (common ports: `80`, `8000`, `8080`, `8899`, `2020`, `443`) |
| `username` | `str ⏐ None` | ❌ No | `None` | Username for device authentication |
| `password` | `str ⏐ None` | ❌ No | `None` | Password for device authentication |

!!! warning
    As of version [`>=v0.3.0`](../releases.md/#v0.3.0), the `username` and `password` parameters are no longer mandatory, in order to maximize compatibility with devices that lack a default user or have no user at all. However, if your device does have a user, you must of course enter the appropriate `username` and `password`.

    Furthermore, this implementation enables the class constructor to perform operations marked as **PRE_AUTH** (according to ONVIF specifications); such as `GetSystemDateAndTime` or `GetCapabilities` within the [`Device`](../api/services/device.md) service that require no authentication.

### Connection Parameters
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `http_digest` | `str` | ❌ No | `False` | `True` = use HTTP Digest / `False` = use WS-UsernameToken (HTTP Digest support from [`>=v0.3.0`](../releases.md/#v0.3.0))[^1] |
| `timeout` | `int` | ❌ No | `10` | Connection timeout in seconds for SOAP requests |
| `use_https` | `bool` | ❌ No | `False` | Use HTTPS instead of HTTP for secure communication |
| `verify_ssl` | `bool` | ❌ No | `False` | Verify SSL certificates when using HTTPS (set to `False` for self-signed certificates) |

### Caching Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `cache` | `CacheMode` | ❌ No | `CacheMode.DB` | WSDL caching strategy (see [**Cache Modes**](#cache-modes) below) |

### Feature Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `apply_patch` | `bool` | ❌ No | `True` | Enable zeep patching for better `xsd:any` field parsing and automatic flattening (applied at [`>=v0.0.4`](../releases.md/#v0.0.4))[^2] |
| `capture_xml` | `bool` | ❌ No | `False` | Enable XML capture plugin for debugging SOAP requests/responses (applied at [`>=v0.0.6`](../releases.md/#v0.0.6))[^3] |
| `wsdl_dir`    | `str ⏐ None`  | ❌ No | `None` | Custom WSDL directory path for using external WSDL files instead of built-in ones (e.g., `/path/to/custom/wsdl`) (applied at [`>=v0.1.0`](../releases.md/#v0.1.0))[^4] |
| `plugins`    | `list[Plugin]`  | ❌ No | `None` | List of user-provided Zeep plugins (`zeep.plugins`) (applied at [`>=v0.2.2`](../releases.md/#v0.2.2)) |

### Cache Modes

The library provides four caching strategies via the [`CacheMode`](../api/utilities/cache_mode.md) enum:

| Mode             | Description                    | Best For                                  | Startup Speed | Disk Usage | Memory Usage |
| ---------------- | ------------------------------ | ----------------------------------------- | ------------- | ---------- | ------------ |
| `CacheMode.DB`   | Persistent disk cache (SQLite)[^5] | Production servers, batch jobs, CLI tools | Fast[^6]         | Low–Medium | Medium       |
| `CacheMode.MEM`  | Process-local in-memory cache  | Long-running apps, short-lived sessions   | Fast[^6]         | None       | Medium       |
| `CacheMode.NONE` | No WSDL/XSD caching            | Testing, debugging                        | Slowest       | None       | Low          |

**Recommendation:**

Use `CacheMode.DB` (default) for production applications to maximize performance[^6].

!!! tip "Version History"
    - Removed in [`>=v0.4.0`](/onvif-python/releases/#v0.4.0): `CacheMode.ALL`

### Usage Examples

#### Basic Connection
```python linenums="1"
from onvif import ONVIFClient

# Minimal configuration
client = ONVIFClient(
    host="192.168.1.17", 
    port=80, 
    username="admin", 
    password="password"
)
```

#### Use HTTP Digest Authentication

Set `http_digest` to `True`. This `http_digest` parameter available since [`>=v0.3.0`](../releases.md/#v0.3.0).

```python linenums="1"
from onvif import ONVIFClient

# Minimal configuration
client = ONVIFClient(
    host="192.168.1.17", 
    port=80, 
    username="admin", 
    password="password",
    http_digest=True  # will use HTTP Digest auth
)
```

#### Secure Connection (HTTPS)
```python linenums="1"
from onvif import ONVIFClient

# Connect via HTTPS with custom timeout
client = ONVIFClient(
    host="your-cctv-node.viewplexus.com", 
    port=443,  # HTTPS port
    username="admin", 
    password="password",
    timeout=30,
    use_https=True
)
```

#### Performance Optimized (Memory Cache)
```python linenums="1"
from onvif import ONVIFClient, CacheMode

# Use memory-only cache for quick scripts
client = ONVIFClient(
    host="192.168.1.17", 
    port=80, 
    username="admin", 
    password="password",
    cache=CacheMode.MEM
)
```

#### No Caching and No Zeep Patching (Testing)
```python linenums="1"
from onvif import ONVIFClient, CacheMode

# Disable all caching for testing
client = ONVIFClient(
    host="192.168.1.17", 
    port=80, 
    username="admin", 
    password="password",
    cache=CacheMode.NONE,
    apply_patch=False  # Use original zeep behavior
)
```

#### Debugging Mode (XML Capture)
```python linenums="1"
from onvif import ONVIFClient

# Enable XML capture for debugging
client = ONVIFClient(
    host="192.168.1.17", 
    port=80, 
    username="admin", 
    password="password",
    capture_xml=True  # Captures all SOAP requests/responses
)

# Make some ONVIF calls
device = client.devicemgmt()
info = device.GetDeviceInformation()
services = device.GetCapabilities()

# Access the XML capture plugin
if client.xml_plugin:
    # Get last captured request/response
    print("Last Request XML:")
    print(client.xml_plugin.last_sent_xml)
    
    print("\nLast Response XML:")
    print(client.xml_plugin.last_received_xml)
    
    print(f"\nLast Operation: {client.xml_plugin.last_operation}")
    
    # Get complete history of all requests/responses
    print(f"\nTotal captured operations: {len(client.xml_plugin.history)}")
    for item in client.xml_plugin.history:
        print(f"  - {item['operation']} ({item['type']})")
    
    # Save captured XML to files
    client.xml_plugin.save_to_file(
        request_file="last_request.xml",
        response_file="last_response.xml"
    )
    
    # Clear history when done
    client.xml_plugin.clear_history()
```

!!! question "XML Capture Plugin"
    To view all available methods and attributes, please refer to [`XMLCapturePlugin`](../api/utilities/plugins.md#onvif.utils.plugins.XMLCapturePlugin).

#### Custom WSDL Directory
```python linenums="1"
from onvif import ONVIFClient

# Use custom WSDL files instead of built-in ones
client = ONVIFClient(
    host="192.168.1.17", 
    port=80, 
    username="admin", 
    password="password",
    wsdl_dir="/path/to/custom/wsdl"  # Custom WSDL directory
)

# All services will automatically use custom WSDL files
device = client.devicemgmt()
media = client.media()
ptz = client.ptz()

# The custom WSDL directory should have a flat structure:
# /path/to/custom/wsdl/
# ├── devicemgmt.wsdl
# ├── media.wsdl
# ├── ptz.wsdl
# ├── imaging.wsdl
# └── ... (other WSDL files)
```

#### Production Configuration

```python linenums="1"
from onvif import ONVIFClient, CacheMode

# Recommended production settings
client = ONVIFClient(
    host="your-cctv-node.viewplexus.com",
    port=443,
    username="admin",
    password="secure_password",
    http_digest=True,           # Use HTTP Digest authentiation
    timeout=15,
    cache=CacheMode.DB,        # Maximum performance (default)
    use_https=True,             # Secure communication
    verify_ssl=True,            # Verify certificates (default)
    apply_patch=True,           # Enhanced parsing (default)
    capture_xml=False,          # Disable debug mode (default)
    wsdl_dir=None               # Use built-in WSDL files (default)
)
```

[^1]:
    This library uses **WS-Security UsernameToken** authentication by default, which is the standard for ONVIF devices.

    You can also use **HTTP Digest** for authentication with `http_digest=True` in [`ONVIFClient`](../api/core/onvif_client.md) constructor, this parameter available since [`>=v0.3.0`](../releases.md/#v0.3.0).
[^2]: 
    The `apply_patch=True` (default) enables custom zeep patching that improves `xsd:any` field parsing. This is recommended for better compatibility with ONVIF responses.
[^3]: Only use `capture_xml=True` during development/debugging as it increases memory usage and may expose sensitive data in logs.
[^4]: 
    Use `wsdl_dir` parameter to specify a custom directory containing WSDL files. 
    
    The directory should have a flat structure with WSDL files directly in the root (e.g., `/path/to/custom/wsdl/devicemgmt.wsdl`, `/path/to/custom/wsdl/media.wsdl`, etc.).
[^5]: Disk cache `CacheMode.DB` is stored in `~/.onvif-python/onvif_zeep_cache.sqlite`.
[^6]: **Fast after the cache is populated**. The first startup may still need to download and parse the WSDL/XSD documents.