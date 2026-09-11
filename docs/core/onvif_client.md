The [`ONVIFClient`](../api/cores/onvif_client.md) class provides various configuration options to customize the connection behavior, caching strategy, security settings, and debugging capabilities. Below is a detailed description of all available parameters:


### Basic Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `host` | `str` | ✅ Yes | - | IP address or hostname of the ONVIF device (e.g., `"192.168.1.17"`) |
| `port` | `int` | ✅ Yes | - | Port number for ONVIF service (common ports: `80`, `8000`, `8080`) |
| `username` | `str` | ❌ No | - | Username for device authentication |
| `password` | `str` | ❌ No | - | Password for device authentication |
| `http_digest` | `str` | ❌ No | `False` | `True` = use HTTP Digest / `False` = use WS-Usernametoken |

### Connection Parameters
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `timeout` | `int` | ❌ No | `10` | Connection timeout in seconds for SOAP requests |
| `use_https` | `bool` | ❌ No | `False` | Use HTTPS instead of HTTP for secure communication |
| `verify_ssl` | `bool` | ❌ No | `False` | Verify SSL certificates when using HTTPS (set to `False` for self-signed certificates) |

### Caching Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `cache` | `CacheMode` | ❌ No | `CacheMode.ALL` | WSDL caching strategy (see **Cache Modes** below) |

### Feature Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `apply_patch` | `bool` | ❌ No | `True` | Enable zeep patching for better `xsd:any` field parsing and automatic flattening, applied at ([`>=v0.0.4`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.0.4)) |
| `capture_xml` | `bool` | ❌ No | `False` | Enable XML capture plugin for debugging SOAP requests/responses, applied at ([`>=v0.0.6`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.0.6)) |
| `wsdl_dir`    | `str`  | ❌ No | `None` | Custom WSDL directory path for using external WSDL files instead of built-in ones (e.g., `/path/to/custom/wsdl`), applied at ([`>=v0.1.0`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.0)) |

### Cache Modes

The library provides four caching strategies via the `CacheMode` enum:

| Mode | Description | Best For | Startup Speed | Disk Usage | Memory Usage |
|------|-------------|----------|---------------|------------|--------------|
| `CacheMode.ALL` | In-memory + disk cache (SQLite) | Production servers, multi-device apps | Fast | High | High |
| `CacheMode.DB` | Disk cache only (SQLite) | Batch jobs, CLI tools | Medium | Medium | Low |
| `CacheMode.MEM` | In-memory cache only | Short-lived scripts, demos | Medium | None | Medium |
| `CacheMode.NONE` | No caching | Testing, debugging | Slow | None | Low |

**Recommendation:** Use `CacheMode.ALL` (default) for production applications to maximize performance.

### Usage Examples

#### Basic Connection
```python
from onvif import ONVIFClient

# Minimal configuration
client = ONVIFClient("192.168.1.17", 80, "admin", "password")
```

#### Secure Connection (HTTPS)
```python
from onvif import ONVIFClient

# Connect via HTTPS with custom timeout
client = ONVIFClient(
    "your-cctv-node.viewplexus.com", 
    443,  # HTTPS port
    "admin", 
    "password",
    timeout=30,
    use_https=True
)
```

#### Performance Optimized (Memory Cache)
```python
from onvif import ONVIFClient, CacheMode

# Use memory-only cache for quick scripts
client = ONVIFClient(
    "192.168.1.17", 
    80, 
    "admin", 
    "password",
    cache=CacheMode.MEM
)
```

#### No Caching and No Zeep Patching (Testing)
```python
from onvif import ONVIFClient, CacheMode

# Disable all caching for testing
client = ONVIFClient(
    "192.168.1.17", 
    80, 
    "admin", 
    "password",
    cache=CacheMode.NONE,
    apply_patch=False  # Use original zeep behavior
)
```

#### Debugging Mode (XML Capture)
```python
from onvif import ONVIFClient

# Enable XML capture for debugging
client = ONVIFClient(
    "192.168.1.17", 
    80, 
    "admin", 
    "password",
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

??? note "XML Capture Plugin Methods"
    - `last_sent_xml` - Get the last SOAP request XML
    - `last_received_xml` - Get the last SOAP response XML
    - `last_operation` - Get the name of the last operation
    - `history` - List of all captured requests/responses with metadata
    - `get_last_request()` - Method to get last request
    - `get_last_response()` - Method to get last response
    - `get_history()` - Method to get all history
    - `save_to_file(request_file, response_file)` - Save XML to files
    - `clear_history()` - Clear captured history

#### Custom WSDL Directory
```python
from onvif import ONVIFClient

# Use custom WSDL files instead of built-in ones
client = ONVIFClient(
    "192.168.1.17", 
    80, 
    "admin", 
    "password",
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

```python
from onvif import ONVIFClient, CacheMode

# Recommended production settings
client = ONVIFClient(
    host="your-cctv-node.viewplexus.com",
    port=443,
    username="admin",
    password="secure_password",
    timeout=15,
    cache=CacheMode.ALL,        # Maximum performance (default)
    use_https=True,             # Secure communication
    verify_ssl=True,            # Verify certificates (default)
    apply_patch=True,           # Enhanced parsing (default)
    capture_xml=False,          # Disable debug mode (default)
    wsdl_dir=None               # Use built-in WSDL files (default)
)
```

### Notes

#### Authentication
This library uses **WS-UsernameToken with Digest** authentication by default, which is the standard for ONVIF devices.

#### Patching
The `apply_patch=True` (default) enables custom zeep patching that improves `xsd:any` field parsing. This is recommended for better compatibility with ONVIF responses.

#### XML Capture
Only use `capture_xml=True` during development/debugging as it increases memory usage and may expose sensitive data in logs.

#### Custom WSDL
Use `wsdl_dir` parameter to specify a custom directory containing WSDL files. The directory should have a flat structure with WSDL files directly in the root (e.g., `/path/to/custom/wsdl/devicemgmt.wsdl`, `/path/to/custom/wsdl/media.wsdl`, etc.).

#### Cache Location
Disk cache (when using `CacheMode.DB` or `CacheMode.ALL`) is stored in `~/.onvif-python/onvif_zeep_cache.sqlite`.