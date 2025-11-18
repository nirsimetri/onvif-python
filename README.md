<h1 align="center">ONVIF Python</h1>

<div align="center">
<a href="https://app.codacy.com/gh/nirsimetri/onvif-python/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade"><img src="https://app.codacy.com/project/badge/Grade/bff08a94e4d447b690cea49c6594826d"/></a>
<a href="https://deepwiki.com/nirsimetri/onvif-python"><img alt="Ask DeepWiki" src="https://deepwiki.com/badge.svg"></a>
<a href="https://pypi.org/project/onvif-python/"><img alt="PyPI Version" src="https://img.shields.io/badge/PyPI-0.2.6-orange?logo=archive&color=yellow"></a>
<a href="https://pepy.tech/projects/onvif-python"><img alt="Pepy Total Downloads" src="https://img.shields.io/pepy/dt/onvif-python?label=Downloads&color=red"></a>
<br>
<a href="https://github.com/nirsimetri/onvif-python/actions/workflows/python-app.yml"><img alt="Build" src="https://github.com/nirsimetri/onvif-python/actions/workflows/python-app.yml/badge.svg?branch=main"></a>
<a href="https://github.com/nirsimetri/onvif-python/actions/workflows/python-publish.yml"><img alt="Upload Python Package" src="https://github.com/nirsimetri/onvif-python/actions/workflows/python-publish.yml/badge.svg"></a>
</div>

<h1 align="center">
  <img src="https://raw.githubusercontent.com/nirsimetri/onvif-python/refs/heads/main/assets/images/carbon_onvif.png" alt="onvif" width="700px">
  <br>
</h1>

**This project provides a comprehensive and developer-friendly Python library for working with ONVIF-compliant devices.** It is designed to be reliable, easy to integrate, and flexible enough to support a wide range of ONVIF profiles and services.  

**[ONVIF](https://www.onvif.org) (Open Network Video Interface Forum)** is a global standard for the interface of IP-based physical security products, including network cameras, video recorders, and related systems.  

Behind the scenes, ONVIF communication relies on **[SOAP](https://en.wikipedia.org/wiki/SOAP) (Simple Object Access Protocol)** — an [XML](https://en.wikipedia.org/wiki/XML)-based messaging protocol with strict schema definitions ([WSDL](https://en.wikipedia.org/wiki/Web_Services_Description_Language)/[XSD](https://en.wikipedia.org/wiki/XML_Schema_(W3C))). SOAP ensures interoperability, but when used directly it can be verbose, complex, and error-prone.  

This library simplifies that process by wrapping SOAP communication into a clean, Pythonic API. You no longer need to handle low-level XML parsing, namespaces, or security tokens manually — the library takes care of it, letting you focus on building functionality.

## Library Philosophy
> [!NOTE]
> This library will be continuously updated as ONVIF versions are updated. It uses a built-in WSDL that will always follow changes to the [ONVIF WSDL Specifications](https://github.com/onvif/specs). You can also use your own ONVIF WSDL file by adding the `wsdl_dir` argument; see [ONVIFClient Parameters](#onvifclient-parameters).

- **WYSIWYG (What You See is What You Get)**: Every ONVIF operation in the library mirrors the official ONVIF specification exactly. Method names, parameter structures, and response formats follow ONVIF standards without abstraction layers or renamed interfaces. What you see in the ONVIF documentation is exactly what you get in Python.

- **Device Variety Interoperability**: Built to handle the real-world diversity of ONVIF implementations across manufacturers. The library gracefully handles missing features, optional operations, and vendor-specific behaviors through comprehensive error handling and fallback mechanisms. Whether you're working with high-end enterprise cameras or budget IP cameras, the library adapts.

- **Official Specifications Accuracy**: All service implementations are generated and validated against official `ONVIF WSDL Specifications`. The library includes comprehensive test suites that verify compliance with ONVIF standards, ensuring that method signatures, parameter types, and behavior match the official specifications precisely.

- **Modern Python Approach**: Designed for excellent IDE support with full type hints, auto-completion, and immediate error detection. You'll get `TypeError` exceptions upfront when accessing ONVIF operations with wrong arguments, instead of cryptic `SOAP faults` later. Clean, Pythonic API that feels natural to Python developers while maintaining ONVIF compatibility.

- **Minimal Dependencies**: Only depends on essential, well-maintained libraries (`zeep` for SOAP, `requests` for HTTP). No bloated framework dependencies or custom XML parsers. The library stays lightweight while providing full ONVIF functionality, making it easy to integrate into any project without dependency conflicts.

## Who Is It For?
- **Individual developers** exploring ONVIF or building hobby projects  
- **Companies** building video intelligence, analytics, or VMS platforms  
- **Security integrators** who need reliable ONVIF interoperability across devices

## Requirements

- **Python**: 3.9 or higher
- **Dependencies**:
  - [`zeep>=4.3.0`](https://github.com/mvantellingen/python-zeep) - SOAP client for ONVIF communication
  - [`requests>=2.32.0`](https://github.com/psf/requests) - HTTP library for network requests

## Installation

From official [PyPI](https://pypi.org/project/onvif-python/):
```bash
pip install --upgrade onvif-python
```
Or clone this repository and install locally:
```bash
git clone https://github.com/nirsimetri/onvif-python
cd onvif-python
pip install .
```

## Usage Example

> [!TIP]
> You can view the complete documentation automatically generated by DeepWiki via the [onvif-python AI Wiki](https://deepwiki.com/nirsimetri/onvif-python) link. We currently do not have an official documentation site. Help us create more examples and helpful documentation by [contributing](https://github.com/nirsimetri/onvif-python?tab=contributing-ov-file).

Below are simple examples to help you get started with the ONVIF Python library. These demonstrate how to discover and connect to ONVIF-compliant devices and retrieve basic device information.

**1. Discover ONVIF Devices (Optional)**

Use `ONVIFDiscovery` (applied at [`>=v0.1.6`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.6)) to automatically find ONVIF devices on your local network:

```python
from onvif import ONVIFDiscovery

# Create discovery instance
discovery = ONVIFDiscovery(timeout=5)

# Discover devices
devices = discovery.discover()

# Or with
# Discover with search filter by types or scopes (case-insensitive substring match)
devices = discovery.discover(search="Profile/Streaming")

# Display discovered devices
for device in devices:
    print(f"Found device at {device['host']}:{device['port']}")
    print(f"  Scopes: {device.get('scopes', [])}")
    print(f"  XAddrs: {device['xaddrs']}")
```

**2. Initialize the ONVIFClient**

Create an instance of `ONVIFClient` by providing your device's IP address, port, username, and password:

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

**3. Create Service Instance**

`ONVIFClient` provides several main services that can be accessed via the following methods:

- `client.devicemgmt()` — Device Management
- `client.events()` — Events
- `client.imaging()` — Imaging
- `client.media()` — Media
- `client.ptz()` — PTZ (Pan-Tilt-Zoom)
- `client.analytics()` — Analytics

and so on, check [Implemented ONVIF Services](https://github.com/nirsimetri/onvif-python?tab=readme-ov-file#implemented-onvif-services) for more details

Example usage:
```python
device = client.devicemgmt()      # Device Management (Core)
media = client.media()            # Media
```

**4. Get Device Information**

Retrieve basic information about the device, such as manufacturer, model, firmware version, and serial number using `devicemgmt()` service:

```python
info = device.GetDeviceInformation()
print(info)
# Example output: {'Manufacturer': '..', 'Model': '..', 'FirmwareVersion': '..', 'SerialNumber': '..'}
```

**5. Get RTSP URL**

Retrieve the RTSP stream URL for live video streaming from the device using `media()` service:

```python
profile = media.GetProfiles()[0]  # use the first profile
stream = media.GetStreamUri(
    ProfileToken=profile.token, 
	StreamSetup={"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}}
)
print(stream)
# Example output: {'Uri': 'rtsp://192.168.1.17:8554/Streaming/Channels/101', ...}
```

Explore more advanced usage and service-specific operations in the [`examples/`](./examples/) folder.

## Helper Methods

Every ONVIF service provides three essential helper methods to improve the development experience and make working with ONVIF operations more intuitive:

**1. `type(type_name)`**

Creates and returns an instance of the specified ONVIF type for building complex request parameters (applied at [`>=v0.1.9`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.9)).

**Usage:**
```python
device = client.devicemgmt()

# Create a new user object
new_user = device.type('CreateUsers')
new_user.User.append({
    "Username": 'new_user', 
    "Password": 'new_password', 
    "UserLevel": 'User'
})
device.CreateUsers(new_user)

# Set hostname
hostname = device.type('SetHostname')
hostname.Name = 'NewHostname'
device.SetHostname(hostname)

# Configure system time
time_params = device.type('SetSystemDateAndTime')
time_params.DateTimeType = 'NTP'
time_params.DaylightSavings = True
time_params.TimeZone.TZ = 'UTC+02:00'
now = datetime.now()
time_params.UTCDateTime.Date.Year = now.year
time_params.UTCDateTime.Date.Month = now.month
time_params.UTCDateTime.Date.Day = now.day
time_params.UTCDateTime.Time.Hour = now.hour
time_params.UTCDateTime.Time.Minute = now.minute
time_params.UTCDateTime.Time.Second = now.second
device.SetSystemDateAndTime(time_params)
```

**2. `operations()`**

Lists all available operations for the current service (applied at [`>=v0.2.0`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.2.0)).

**Returns:**
- List of operation names that can be called on the service

**Usage:**
```python
device = client.devicemgmt()
media = client.media()
ptz = client.ptz()

# List all available operations for each service
print("Device Management Operations:")
for op in device.operations():
    print(f"  - {op}")

print("\nMedia Operations:")
for op in media.operations():
    print(f"  - {op}")

print("\nPTZ Operations:")
for op in ptz.operations():
    print(f"  - {op}")

# Check if specific operation is supported
if 'ContinuousMove' in ptz.operations():
    print("PTZ continuous movement is supported")
```

**3. `desc(method_name)`**

Provides comprehensive documentation and parameter information for any ONVIF operation (applied at [`>=v0.2.0`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.2.0)).

**Returns:**
- `doc`: Method documentation from WSDL
- `required`: List of required parameter names
- `optional`: List of optional parameter names
- `method_name`: The method name
- `service_name`: The service name

**Usage:**
```python
device = client.devicemgmt()

# Get detailed information about a method
info = device.desc('GetDeviceInformation')
print(info['doc'])
print("Required params:", info['required'])
print("Optional params:", info['optional'])

# Explore available methods first
methods = device.operations()
for method in methods[:5]:  # Show first 5 methods
    info = device.desc(method)
    print(f"{method}: {len(info['required'])} required, {len(info['optional'])} optional")
```

> [!TIP]
> These helper methods are available on **all** ONVIF services (`devicemgmt()`, `media()`, `ptz()`, `events()`, `imaging()`, `analytics()`, etc.) and provide a consistent API for exploring and using ONVIF capabilities across different device types and manufacturers.

> [!IMPORTANT]
> If you're new to ONVIF and want to learn more, we highly recommend taking the official free online course provided by ONVIF at [Introduction to ONVIF Course](https://www.onvif.org/about/introduction-to-onvif-course). Please note that we are not endorsed or sponsored by ONVIF, see [Legal Notice](#legal-notice) for details.

## ONVIF CLI

> [!NOTE]
> The CLI is automatically installed when you install the `onvif-python` see [Installation](#installation). This feature has been available since `onvif-python` version [`>=0.1.1`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.1).

![Windows](https://img.shields.io/badge/Windows-0078D6?style=plastic&logo=gitforwindows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=plastic&logo=linux&logoColor=black)
![macOS](https://img.shields.io/badge/macOS-1A9FEE?style=plastic&logo=apple&logoColor=black)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=plastic&logo=raspberrypi&logoColor=black)

This library includes a powerful command-line interface (CLI) for interacting with ONVIF devices directly from your terminal. It supports both direct command execution and an interactive shell mode, providing a flexible and efficient way to manage and debug ONVIF devices.

### Features

- **Device Discovery:** Automatic ONVIF device discovery on local network using WS-Discovery protocol.
- **Interactive Shell:** A user-friendly shell with tab completion, command history, and colorized output.
- **Direct Command Execution:** Run ONVIF commands directly from the terminal for scripting and automation.
- **Automatic Discovery:** Automatically detects available services on the device.
- **Connection Management:** Supports HTTP/HTTPS, custom timeouts, and SSL verification.
- **Data Management:** Store results from commands and use them as parameters in subsequent commands.
- **Cross-Platform:** Works on Windows, macOS, Linux, and Raspberry Pi.

### Screenshoot

<table>
  <tr>
    <td width="34.2%">
      <a href="https://github.com/nirsimetri/onvif-python">
        <img src="https://raw.githubusercontent.com/nirsimetri/onvif-python/refs/heads/main/assets/images/onvif_cli.png" />
      </a>
    </td>
    <td width="65.8%">
        <a href="https://github.com/nirsimetri/onvif-python">
        <img src="https://raw.githubusercontent.com/nirsimetri/onvif-python/refs/heads/main/assets/images/onvif_operations.png" />
        </a>
    </td>
  </tr>
  <tr>
    <th align="center">
      Onboarding
    </th>
    <th align="center">
      List available operations
    </th>
  </tr>
</table>

### Help Command

<details>
<summary><b>1. Direct CLI</b></summary> 

```bash
usage: onvif [-h] [--host HOST] [--port PORT] [--username USERNAME] [--password PASSWORD] [--discover] [--filter FILTER] [--search SEARCH] [--page PAGE]
             [--per-page PER_PAGE] [--timeout TIMEOUT] [--https] [--no-verify] [--no-patch] [--interactive] [--debug] [--wsdl WSDL]
             [--cache {all,db,mem,none}] [--health-check-interval HEALTH_CHECK_INTERVAL] [--output OUTPUT] [--version]
             [service] [method] [params ...]

ONVIF Terminal Client — v0.2.6
https://github.com/nirsimetri/onvif-python

positional arguments:
  service               ONVIF service name (e.g., devicemgmt, media, ptz)
  method                Service method name (e.g., GetCapabilities, GetProfiles)
  params                Method parameters as Simple Parameter or JSON string

options:
  -h, --help            show this help message and exit
  --host HOST, -H HOST  ONVIF device IP address or hostname
  --port PORT, -P PORT  ONVIF device port (default: 80)
  --username USERNAME, -u USERNAME
                        Username for authentication
  --password PASSWORD, -p PASSWORD
                        Password for authentication
  --discover, -d        Discover ONVIF devices on the network using WS-Discovery
  --filter FILTER, -f FILTER
                        Filter discovered devices by types or scopes (case-insensitive substring match)
  --search SEARCH, -s SEARCH
                        Search ONVIF products database by model or company (e.g., 'c210', 'hikvision')
  --page PAGE           Page number for search results (default: 1)
  --per-page PER_PAGE   Number of results per page (default: 20)
  --timeout TIMEOUT     Connection timeout in seconds (default: 10)
  --https               Use HTTPS instead of HTTP
  --no-verify           Disable SSL certificate verification
  --no-patch            Disable ZeepPatcher
  --interactive, -i     Start interactive mode
  --debug               Enable debug mode with XML capture
  --wsdl WSDL           Custom WSDL directory path
  --cache {all,db,mem,none}
                        Caching mode for ONVIFClient (default: all). 'all': memory+disk, 'db': disk-only, 'mem': memory-only, 'none': disabled.
  --health-check-interval HEALTH_CHECK_INTERVAL, -hci HEALTH_CHECK_INTERVAL
                        Health check interval in seconds for interactive mode (default: 10)
  --output OUTPUT, -o OUTPUT
                        Save command output to file. Supports .json, .xml extensions for format detection, or plain text. XML format automatically enables
                        debug mode for SOAP capture.
  --version, -v         Show ONVIF CLI version and exit

Examples:
  # Product search
  onvif --search c210
  onvif -s "axis camera"
  onvif --search hikvision --page 2 --per-page 5

  # Discover ONVIF devices on network
  onvif --discover --username admin --password admin123 --interactive
  onvif media GetProfiles --discover --username admin
  onvif -d -i

  # Discover with filtering
  onvif --discover --filter ptz --interactive
  onvif -d -f "C210" -i
  onvif -d -f "audio_encoder" -u admin -p admin123 -i

  # Direct command execution
  onvif devicemgmt GetCapabilities Category=All --host 192.168.1.17 --port 8000 --username admin --password admin123
  onvif ptz ContinuousMove ProfileToken=Profile_1 Velocity={'PanTilt': {'x': -0.1, 'y': 0}} -H 192.168.1.17 -P 8000 -u admin -p admin123

  # Save output to file
  onvif devicemgmt GetDeviceInformation --host 192.168.1.17 --port 8000 --username admin --password admin123 --output device_info.json
  onvif media GetProfiles --host 192.168.1.17 --port 8000 --username admin --password admin123 --output profiles.xml
  onvif ptz GetConfigurations --host 192.168.1.17 --port 8000 --username admin --password admin123 --output ptz_config.txt --debug

  # Interactive mode
  onvif --host 192.168.1.17 --port 8000 --username admin --password admin123 --interactive

  # Prompting for username and password
  # (if not provided)
  onvif -H 192.168.1.17 -P 8000 -i

  # Using HTTPS
  onvif media GetProfiles --host camera.example.com --port 443 --username admin --password admin123 --https
```

</details>

<details>
<summary><b>2. Interactive Shell</b></summary> 

```bash
ONVIF Interactive Shell — v0.2.6
https://github.com/nirsimetri/onvif-python

Basic Commands:
  capabilities, caps       - Show device capabilities
  services                 - Show available services with details
  info                     - Show connection and device information
  exit, quit               - Exit the shell
  shortcuts                - Show available shortcuts

Navigation Commands:
  <service>                - Enter service mode (e.g., devicemgmt, media)
  <service> <argument>     - Enter service mode with argument (e.g. pullpoint SubscriptionRef=<value>)
  cd <service>             - Enter service mode (alias)
  ls                       - List commands/services/methods in grid format
  up                       - Exit current service mode (go up one level)
  pwd                      - Show current service context
  clear                    - Clear terminal screen
  help <command>           - Show help for a specific command

Service Mode Commands:
  desc <method>            - Show method documentation
  type <method>            - Show input/output types from WSDL

Method Execution:
  <method>                 - Execute method without parameters
  <method> {"param": "value"}  - Execute method with JSON parameters
  <method> param=value     - Execute method with simple parameters

Data Management:
  store <name>             - Store last result with a name
  show <name>              - Show stored data
  show <name>[0]           - Show element at index (for lists)
  show <name>.attribute    - Show specific attribute
  show                     - List all stored data
  rm <name>                - Remove stored data by name
  cls                      - Clear all stored data

Using Stored Data in Methods:
  Use $variable syntax to reference stored data in method parameters:
  - $profiles[0].token                    - Access list element and attribute
  - $profiles[0].VideoSourceConfiguration.SourceToken

  Example:
    GetProfiles                           - Get profiles
    store profiles                        - Store result
    show profiles[0].token                - Show first profile token
    GetImagingSettings VideoSourceToken=$profiles[0].VideoSourceConfiguration.SourceToken

Debug Commands:
  debug                    - Show last SOAP request & response (if --debug enabled)

Tab Completion:
  Use TAB key for auto-completion of commands, services, and methods
  Type partial commands to see suggestions

Examples:
  192.168.1.17:8000 > caps                # Show capabilities
  192.168.1.17:8000 > dev<TAB>            # Completes to 'devicemgmt'
  192.168.1.17:8000 > cd devicemgmt       # Enter device management
  192.168.1.17:8000/devicemgmt > Get<TAB> # Show methods starting with 'Get'
  192.168.1.17:8000/devicemgmt > GetServices {"IncludeCapability": true}
  192.168.1.17:8000/devicemgmt > GetServices IncludeCapability=True
  192.168.1.17:8000/devicemgmt > store services_info
  192.168.1.17:8000/devicemgmt > up       # Exit service mode
  192.168.1.17:8000 >                     # Back to root context
```

</details>

### Usage

**1. Interactive Mode**

The interactive shell is recommended for exploration and debugging. It provides an intuitive way to navigate services, call methods, and view results.

To start the interactive shell, provide the connection details:

```bash
onvif --host 192.168.1.17 --port 8000 --username admin --password admin123 -i
```

If you omit the username or password, you will be prompted to enter them securely.

**Interactive Shell Commands:**
| Command | Description |
|---|---|
| `help` | Show help information |
| `ls` | List available services or methods in the current context |
| `cd <service>` | Enter a service mode (e.g., `cd devicemgmt`) |
| `up` | Go back to the root context |
| `pwd` | Show the current service context |
| `desc <method>` | Show documentation for a method |
| `store <name>` | Store the last result with a variable name |
| `show <name>` | Display a stored variable |
| `exit` / `quit` | Exit the shell |

> [!IMPORTANT]
> You can see all the other commands available in the interactive shell by trying it out directly. The interactive shell runs periodic background health checks to detect connection loss. It uses silent TCP pings to avoid interrupting your work and will automatically exit if the device is unreachable, similar to an SSH session.

**Command Chaining with `&&`:**

The CLI supports chaining multiple commands in a single line using the `&&` operator, allowing you to execute sequential operations efficiently:

```bash
# Enter service and execute method in one line
192.168.1.17:8000 > media && GetProfiles && store profiles

# Chain multiple method calls
192.168.1.17:8000 > devicemgmt && GetDeviceInformation && store device_info

# Complex workflow
192.168.1.17:8000 > media && GetProfiles && store profiles && up && imaging && GetImagingSettings VideoSourceToken=$profiles[0].VideoSourceConfiguration.SourceToken
```

This feature is particularly useful for:
- Quick operations without entering service mode
- Scripting repetitive tasks
- Testing workflows
- Automating multi-step procedures

**2. Device Discovery (WS-Discovery)**

The CLI includes automatic ONVIF device discovery using the WS-Discovery protocol. This feature allows you to find all ONVIF-compliant devices on your local network without knowing their IP addresses beforehand (applied at [`>=v0.1.2`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.2)).

**Discover and Connect Interactively:**
```bash
# Discover devices and enter interactive mode
onvif --discover --username admin --password admin123 --interactive

# Short form
onvif -d -u admin -p admin123 -i

# Discover with search filter
onvif --discover --filter "C210" --interactive
onvif -d -f ptz -u admin -p admin123 -i

# Discover and interactive (will prompt for credentials)
onvif -d -i
```

**Discover and Execute Command:**
```bash
# Discover devices and execute a command on the selected device
onvif media GetProfiles --discover --username admin --password admin123

# Short form
onvif media GetProfiles -d -u admin -p admin123
```

**How Device Discovery Works:**

1. **Automatic Network Scanning**: Sends a WS-Discovery Probe message to the multicast address `239.255.255.250:3702`
2. **Device Detection**: Listens for ProbeMatch responses from ONVIF devices (default timeout: 4 seconds)
3. **Interactive Selection**: Displays a numbered list of discovered devices with their details:
   - Device UUID (Endpoint Reference)
   - XAddrs (ONVIF service URLs)
   - Device Types (e.g., NetworkVideoTransmitter)
   - Scopes (name, location, hardware, profile information)
4. **Connection**: Once you select a device, the CLI automatically connects using the discovered host and port

**Example Discovery Output:**
```
Discovering ONVIF devices on network...
Network interface: 192.168.1.100
Timeout: 4s

Found 2 ONVIF device(s):

[1] 192.168.1.14:2020
    [id] 3fa1fe68-b915-4053-a3e1-a8294833fe3c
    [xaddrs] [http://192.168.1.14:2020/onvif/device_service]
    [types] [tdn:NetworkVideoTransmitter]
    [scopes] [name/C210] [hardware/C210] [Profile/Streaming] [location/Hong Kong]

[2] 192.168.1.17:8000
    [id] 7d04ff31-61e6-11f0-a00c-6056eef47207
    [xaddrs] [http://192.168.1.17:8000/onvif/device_service]
    [types] [dn:NetworkVideoTransmitter] [tds:Device]
    [scopes] [type/NetworkVideoTransmitter] [location/unknown] [name/IPC_123465959]

Select device number 1-2 or q to quit: 1

Selected: 192.168.1.14:2020
```

**Notes:**

- Discovery only works on the local network (same subnet)
- Some networks may block multicast traffic (check firewall settings)
- The `--host` and `--port` arguments are not required when using `--discover`
- You can still provide `--username` and `--password` upfront to avoid prompts

**3. Direct Command Execution**

You can also execute a single ONVIF command directly. This is useful for scripting or quick checks.

**Syntax:**
```bash
onvif <service> <method> [parameters...] -H <host> -P <port> -u <user> -p <pass>
```

**Example:**
```bash
# Get device capabilities
onvif devicemgmt GetCapabilities Category=All -H 192.168.1.17 -P 8000 -u admin -p admin123

# Move a PTZ camera
onvif ptz ContinuousMove ProfileToken=Profile_1 Velocity='{"PanTilt": {"x": 0.1, "y": 0}}' -H 192.168.1.17 -P 8000 -u admin -p admin123

# Save output to file
onvif devicemgmt GetDeviceInformation --host 192.168.1.17 --port 8000 --username admin --password admin123 --output device_info.json
onvif media GetProfiles -H 192.168.1.17 -P 8000 -u admin -p admin123 -o profiles.xml
```

**4. ONVIF Product Search**

The CLI includes a built-in database of ONVIF-compatible products that can be searched to help identify and research devices before connecting (applied at [`>=v0.2.0`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.2.0)).

**Basic Search:**
```bash
# Search by model name
onvif --search "C210"
onvif -s "axis camera"

# Search by manufacturer
onvif --search "hikvision"
onvif -s "dahua"

# Search by any keyword
onvif --search "ptz"
onvif -s "thermal"
```

**Paginated Results:**
```bash
# Navigate through multiple pages of results
onvif --search "hikvision" --page 2 --per-page 5
onvif -s "axis" --page 1 --per-page 10

# Adjust results per page (1-100)
onvif --search "camera" --per-page 20
```

**Search Database Information:**

The product database contains comprehensive information about tested ONVIF devices:

| Field | Description |
|-------|-------------|
| **ID** | Unique product identifier |
| **Test Date** | When the device was last tested/verified |
| **Model** | Device model name and number |
| **Firmware** | Tested firmware version |
| **Profiles** | Supported ONVIF profiles (S, G, T, C, A, etc.) |
| **Category** | Device type (Camera, NVR, etc.) |
| **Type** | Specific device classification |
| **Company** | Manufacturer name |

**Example Output:**
```
Found 15 product(s) matching: hikvision
Showing 1-10 of 15 results

ID  | Test Date           | Model             | Firmware | Profiles | Category | Type    | Company
----|---------------------|-------------------|----------|----------|----------|---------|---------
342 | 2024-08-15 17:53:12 | DS-2CD2143G2-IU   | V5.7.3   | S,G,T    | Camera   | device  | Hikvision
341 | 2024-08-14 14:22:05 | DS-2DE2A404IW-DE3 | V5.6.15  | S,G,T    | Camera   | device  | Hikvision
...

Page 1 of 2
Navigation: Next: --page 2
```

### CLI Parameters

All `ONVIFClient` parameters (like `--timeout`, `--https`, `--cache`, etc.) are available as command-line arguments. Use `onvif --help` to see all available options.

## ONVIFClient Parameters

The `ONVIFClient` class provides various configuration options to customize the connection behavior, caching strategy, security settings, and debugging capabilities. Below is a detailed description of all available parameters:


<details>
<summary><b>Basic Parameters</b></summary>

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `host` | `str` | ✅ Yes | - | IP address or hostname of the ONVIF device (e.g., `"192.168.1.17"`) |
| `port` | `int` | ✅ Yes | - | Port number for ONVIF service (common ports: `80`, `8000`, `8080`) |
| `username` | `str` | ✅ Yes | - | Username for device authentication (use digest authentication) |
| `password` | `str` | ✅ Yes | - | Password for device authentication |

</details>

<details>
<summary><b>Connection Parameters</b></summary>

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `timeout` | `int` | ❌ No | `10` | Connection timeout in seconds for SOAP requests |
| `use_https` | `bool` | ❌ No | `False` | Use HTTPS instead of HTTP for secure communication |
| `verify_ssl` | `bool` | ❌ No | `True` | Verify SSL certificates when using HTTPS (set to `False` for self-signed certificates) |

</details>

<details>
<summary><b>Caching Parameters</b></summary>

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `cache` | `CacheMode` | ❌ No | `CacheMode.ALL` | WSDL caching strategy (see **Cache Modes** below) |

</details>

<details>
<summary><b>Feature Parameters</b></summary>

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `apply_patch` | `bool` | ❌ No | `True` | Enable zeep patching for better `xsd:any` field parsing and automatic flattening, applied at ([`>=v0.0.4`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.0.4)) |
| `capture_xml` | `bool` | ❌ No | `False` | Enable XML capture plugin for debugging SOAP requests/responses, applied at ([`>=v0.0.6`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.0.6)) |
| `wsdl_dir`    | `str`  | ❌ No | `None` | Custom WSDL directory path for using external WSDL files instead of built-in ones (e.g., `/path/to/custom/wsdl`), applied at ([`>=v0.1.0`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.0)) |

</details>

<details>
<summary><b>Cache Modes</b></summary> 

The library provides four caching strategies via the `CacheMode` enum:

| Mode | Description | Best For | Startup Speed | Disk Usage | Memory Usage |
|------|-------------|----------|---------------|------------|--------------|
| `CacheMode.ALL` | In-memory + disk cache (SQLite) | Production servers, multi-device apps | Fast | High | High |
| `CacheMode.DB` | Disk cache only (SQLite) | Batch jobs, CLI tools | Medium | Medium | Low |
| `CacheMode.MEM` | In-memory cache only | Short-lived scripts, demos | Medium | None | Medium |
| `CacheMode.NONE` | No caching | Testing, debugging | Slow | None | Low |

**Recommendation:** Use `CacheMode.ALL` (default) for production applications to maximize performance.

</details>

<details>
<summary><b>Usage Examples</b></summary>

**Basic Connection:**
```python
from onvif import ONVIFClient

# Minimal configuration
client = ONVIFClient("192.168.1.17", 80, "admin", "password")
```

**Secure Connection (HTTPS):**
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

**Performance Optimized (Memory Cache):**
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

**No Caching and No Zeep Patching (Testing):**
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

**Debugging Mode (XML Capture):**
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

> **XML Capture Plugin Methods:**
> - `last_sent_xml` - Get the last SOAP request XML
> - `last_received_xml` - Get the last SOAP response XML
> - `last_operation` - Get the name of the last operation
> - `history` - List of all captured requests/responses with metadata
> - `get_last_request()` - Method to get last request
> - `get_last_response()` - Method to get last response
> - `get_history()` - Method to get all history
> - `save_to_file(request_file, response_file)` - Save XML to files
> - `clear_history()` - Clear captured history

**Custom WSDL Directory:**
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

</details>

<details>
<summary><b>Production Configuration</b></summary>

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
</details>

### Notes

- **Authentication:** This library uses **WS-UsernameToken with Digest** authentication by default, which is the standard for ONVIF devices.
- **Patching:** The `apply_patch=True` (default) enables custom zeep patching that improves `xsd:any` field parsing. This is recommended for better compatibility with ONVIF responses.
- **XML Capture:** Only use `capture_xml=True` during development/debugging as it increases memory usage and may expose sensitive data in logs.
- **Custom WSDL:** Use `wsdl_dir` parameter to specify a custom directory containing WSDL files. The directory should have a flat structure with WSDL files directly in the root (e.g., `/path/to/custom/wsdl/devicemgmt.wsdl`, `/path/to/custom/wsdl/media.wsdl`, etc.).
- **Cache Location:** Disk cache (when using `CacheMode.DB` or `CacheMode.ALL`) is stored in `~/.onvif-python/onvif_zeep_cache.sqlite`.

## Service Discovery: Understanding Device Capabilities

> [!WARNING]
> Before performing any operations on an ONVIF device, it is highly recommended to discover which services are available and supported by the device. This library automatically performs comprehensive service discovery during initialization using a robust fallback mechanism.

**Why discover device services?**

- **Device Diversity:** Not all ONVIF devices support every service. Available services may vary by manufacturer, model, firmware, or configuration.
- **Error Prevention:** Attempting to use unsupported services can result in failed requests, exceptions, or undefined behavior.
- **Dynamic Feature Detection:** Devices may enable or disable services over time (e.g., after firmware updates or configuration changes).
- **Optimized Integration:** By checking available services, your application can adapt its workflow and UI to match the device's actual features.

**How service discovery works in this library:**

The `ONVIFClient` uses a **3-tier discovery approach** to maximize device compatibility:

1. **GetServices (Preferred)** - Tries `GetServices` first for detailed service information
2. **GetCapabilities (Fallback)** - Falls back to `GetCapabilities` if `GetServices` is not supported
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

**Why this approach?**

- **GetServices** provides the most accurate and detailed service information, but it's **optional** in the ONVIF specification
- **GetCapabilities** is **mandatory** for all ONVIF-compliant devices, ensuring broader compatibility
- **Default URLs** guarantee basic connectivity even with non-compliant devices

> [!TIP]
> The library handles service discovery automatically with intelligent fallback. You typically don't need to call discovery methods manually unless you need detailed capability information or want to refresh the service list after device configuration changes.

## Tested Devices

This library has been tested with a variety of ONVIF-compliant devices. For the latest and most complete list of devices that have been verified to work with this library, please refer to:

- [List of tested devices (device-test)](https://github.com/nirsimetri/onvif-products-directory/blob/main/device-test)

If your device is not listed right now, feel free to contribute your test results or feedback via Issues or Discussions at [onvif-products-directory](https://github.com/nirsimetri/onvif-products-directory). Your contribution will be invaluable to the community and the public.

> [!IMPORTANT]
> Device testing contributions must be made with a real device and use the scripts provided in the [onvif-products-directory](https://github.com/nirsimetri/onvif-products-directory) repo. Please be sure to contribute using a device model not already listed.

## Supported ONVIF Profiles

This library fully supports all major ONVIF Profiles listed below. Each profile represents a standardized set of features and use cases, ensuring interoperability between ONVIF-compliant devices and clients. You can use this library to integrate with devices and systems that implement any of these profiles.

<details>
<summary><b>ONVIF profiles list</b></summary>

| Name      | Specifications | Main Features | Typical Use Case | Support |
|-----------|----------------|---------------|------------------|---------|
| Profile_S | [Document](https://www.onvif.org/wp-content/uploads/2019/12/ONVIF_Profile_-S_Specification_v1-3.pdf) | Video streaming, PTZ, audio, multicasting | Network video transmitters (cameras) and receivers (recorders, VMS) | ✅ Yes |
| Profile_G | [Document](https://www.onvif.org/wp-content/uploads/2017/01/ONVIF_Profile_G_Specification_v1-0.pdf) | Recording, search, replay, video storage | Video recorders, storage devices | ✅ Yes |
| Profile_T | [Document](https://www.onvif.org/wp-content/uploads/2018/09/ONVIF_Profile_T_Specification_v1-0.pdf) | Advanced video streaming (H.265, analytics metadata, motion detection) | Modern cameras and clients | ✅ Yes |
| Profile_C | [Document](https://www.onvif.org/wp-content/uploads/2017/01/2013_12_ONVIF_Profile_C_Specification_v1-0.pdf) | Access control, door monitoring | Door controllers, access systems | ✅ Yes |
| Profile_A | [Document](https://www.onvif.org/wp-content/uploads/2017/06/ONVIF_Profile_A_Specification_v1-0.pdf) | Advanced access control configuration, credential management | Access control clients and devices | ✅ Yes |
| Profile_D | [Document](https://www.onvif.org/wp-content/uploads/2021/06/onvif-profile-d-specification-v1-0.pdf) | Access control peripherals (locks, sensors, relays) | Peripheral devices for access control | ✅ Yes |
| Profile_M | [Document](https://www.onvif.org/wp-content/uploads/2024/04/onvif-profile-m-specification-v1-1.pdf) | Metadata, analytics events, object detection | Analytics devices, metadata clients | ✅ Yes |

</details>

For a full description of each profile and its features, visit [ONVIF Profiles](https://www.onvif.org/profiles/).

## Implemented ONVIF Services

> [!NOTE]
> For details about the available service functions and methods already implemented in this library, see the source code in [`onvif/services/`](./onvif/services). Or if you want to read in a more proper format visit [onvif-python AI Wiki](https://deepwiki.com/nirsimetri/onvif-python).

Below is a list of ONVIF services implemented and supported by this library, along with links to the official specifications, service definitions, and schema files as referenced from the [ONVIF Developer Specs](https://developer.onvif.org/pub/specs/branches/development/doc/index.html). This table provides a quick overview of the available ONVIF features and their technical documentation for integration and development purposes.

<details>
<summary><b>ONVIF services list</b></summary>

| Service                | Specifications                | Service Definitions         | Schema Files                        | Status     |
|------------------------|-------------------------------|-----------------------------|-------------------------------------|------------|
| Device Management      | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Core.xml)                   | [device.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/device/wsdl/devicemgmt.wsdl)    | [onvif.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schema/onvif.xsd) <br> [common.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schema/common.xsd)                | ✅ Complete |
| Events                 | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Core.xml)                   | [event.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/events/wsdl/event.wsdl)    | [onvif.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schema/onvif.xsd) <br> [common.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schema/common.xsd)                | ✅ Complete |
| Access Control         | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/AccessControl.xml)         | [accesscontrol.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/pacs/accesscontrol.wsdl)         | [types.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/pacs/types.xsd)                            | ✅ Complete |
| Access Rules           | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/AccessRules.xml)           | [accessrules.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/accessrules/wsdl/accessrules.wsdl)           | -                                      | ✅ Complete |
| Action Engine          | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/ActionEngine.xml)          | [actionengine.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/actionengine.wsdl)          | -                                      | ✅ Complete |
| Analytics              | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Analytics.xml)             | [analytics.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/wsdl/analytics.wsdl)             | [rules.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/rules.xsd) <br> [humanbody.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/humanbody.xsd) <br> [humanface.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/humanface.xsd) | ✅ Complete |
| Analytics Device       | [Document](https://www.onvif.org/specs/srv/analytics/ONVIF-VideoAnalyticsDevice-Service-Spec-v211.pdf) | [analyticsdevice.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/analyticsdevice.wsdl)             | - | ✅ Complete |
| Application Management | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/AppMgmt.xml)               | [appmgmt.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/appmgmt/wsdl/appmgmt.wsdl)               | -                                     | ✅ Complete |
| Authentication Behavior| [Document](https://developer.onvif.org/pub/specs/branches/development/doc/AuthenticationBehavior.xml) | [authenticationbehavior.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/authenticationbehavior/wsdl/authenticationbehavior.wsdl) | -                                     | ✅ Complete |
| Cloud Integration      | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/CloudIntegration.xml)      | [cloudintegration.yaml](https://developer.onvif.org/pub/specs/branches/development/doc/yaml.php?yaml=cloudintegration.yaml)      | -                                     | ❌ Not yet |
| Credential             | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Credential.xml)            | [credential.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/credential/wsdl/credential.wsdl)            | -                                     | ✅ Complete |
| Device IO              | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/DeviceIo.xml)              | [deviceio.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/deviceio.wsdl)              |-                                      | ✅ Complete |
| Display                | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Display.xml)               | [display.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/display.wsdl)               | -                                     | ✅ Complete |
| Door Control           | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/DoorControl.xml)           | [doorcontrol.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/pacs/doorcontrol.wsdl)           | -                                     | ✅ Complete |
| Imaging                | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Imaging.xml)               | [imaging.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/imaging/wsdl/imaging.wsdl)               | -                                     | ✅ Complete |
| Media                  | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Media.xml)                 | [media.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/media/wsdl/media.wsdl)                 | -                                     | ✅ Complete |
| Media 2                | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Media2.xml)                | [media2.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/media/wsdl/media.wsdl)                | -                                     | ✅ Complete |
| Provisioning           | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Provisioning.xml)          | [provisioning.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/provisioning/wsdl/provisioning.wsdl)          | -                                     | ✅ Complete |
| PTZ                    | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/PTZ.xml)                    | [ptz.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/ptz/wsdl/ptz.wsdl)                   | -                                     | ✅ Complete |
| Receiver               | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Receiver.xml)               | [receiver.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/receiver.wsdl)              | -                                     | ✅ Complete |
| Recording Control      | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/RecordingControl.xml)       | [recording.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/recording.wsdl)             | -                                     | ✅ Complete |
| Recording Search       | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/RecordingSearch.xml)        | [search.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/search.wsdl)                | -                                     | ✅ Complete |
| Replay Control         | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Replay.xml)                 | [replay.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/replay.wsdl)                | -                                     | ✅ Complete |
| Schedule               | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Schedule.xml)               | [schedule.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schedule/wsdl/schedule.wsdl)              | -                                     | ✅ Complete |
| Security               | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Security.xml)               | [advancedsecurity.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)      | -                                     | ✅ Complete |
| Thermal                | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Thermal.xml)                | [thermal.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/thermal/wsdl/thermal.wsdl)               | [radiometry.xsd](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/radiometry.xsd)                       | ✅ Complete |
| Uplink                 | [Document](https://developer.onvif.org/pub/specs/branches/development/doc/Uplink.xml)                 | [uplink.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/uplink/wsdl/uplink.wsdl)                | -                                     | ✅ Complete |

</details>

## Service Bindings in ONVIF

ONVIF services are defined by WSDL bindings. In this library, there are two main patterns:

### 1. Single Binding Services

Most ONVIF services use a single binding, mapping directly to one endpoint. These are accessed via simple client methods, and the binding/xAddr is always known from device capabilities.

<details>
<summary>Examples:</summary>

```python
client.devicemgmt()   # DeviceBinding
client.media()        # MediaBinding
client.ptz()          # PTZBinding
...
```

✅ These are considered fixed and always accessed directly.

</details>

### 2. Multi-Binding Services

Some ONVIF services have multiple bindings in the same WSDL. These typically include:
- A **root binding** (main entry point)
- One or more **sub-bindings**, discovered or created dynamically (e.g. after subscription/configuration creation)

<details>
<summary>Examples:</summary>

1. **Events**
   - **Root:** `EventBinding`
   - **Sub-bindings:**
     - `PullPointSubscriptionBinding` (created via `CreatePullPointSubscription`)
     - `SubscriptionManagerBinding` (manages existing subscriptions)
     - `NotificationProducerBinding`

   Usage in library:
   ```python
   client.events()                    # root binding
   client.pullpoint(subscription)     # sub-binding (dynamic, via SubscriptionReference.Address)
   client.subscription(subscription)  # sub-binding (dynamic, via SubscriptionReference.Address)
   client.notification()              # sub-binding accessor
   ```

2. **Security (Advanced Security)**
   - **Root:** `AdvancedSecurityServiceBinding`
   - **Sub-bindings:**
     - `JWTBinding`
     - `AuthorizationServerBinding`
     - `KeystoreBinding`
     - `Dot1XBinding`
     - `TLSServerBinding`
     - `MediaSigningBinding`

   Usage in library:
   ```python
   client.security()                  # root binding
   client.jwt()                       # sub-binding accessor
   client.authorizationserver(xaddr)  # sub-binding accessor (requires xAddr)
   client.keystore(xaddr)             # ..
   client.dot1x(xaddr)
   client.tlsserver(xaddr)
   client.mediasigning(xaddr)
   ```

3. **Analytics**
   - **Root:** `AnalyticsEngineBinding`
   - **Sub-bindings:**
     - `RuleEngineBinding`

   Usage in library:
   ```python
   client.analytics()   # root binding
   client.ruleengine()  # sub-binding accessor
   ```
</details>

### Summary

- **Single binding services:** Always accessed directly (e.g. `client.media()`).
- **Multi-binding services:** Have a root + sub-binding(s). Root is fixed; sub-bindings may require dynamic creation or explicit xAddr (e.g. `client.pullpoint(subscription)`, `client.authorizationserver(xaddr)`).

## Future Improvements (Stay tuned and star ⭐ this repo)

- [x] ~~Add debugging mode with raw xml on SOAP requests and responses.~~ ([c258162](https://github.com/nirsimetri/onvif-python/commit/c258162))
- [x] ~~Add functionality for `ONVIFClient` to accept a custom `wsdl_dir` service.~~ ([65f2570](https://github.com/nirsimetri/onvif-python/commit/65f2570))
- [x] ~~Add `ONVIF CLI` program to interact directly with ONVIF devices via terminal.~~ ([645be01](https://github.com/nirsimetri/onvif-python/commit/645be01))
- [ ] Add asynchronous (async/await) support for non-blocking ONVIF operations and concurrent device communication.
- [ ] Implement structured data models for ONVIF Schemas using [xsdata](https://github.com/tefra/xsdata).
- [ ] Integrate [xmltodict](https://github.com/martinblech/xmltodict) for simplified XML parsing and conversion.
- [ ] Enhance documentation with API references and diagrams (not from [AI Wiki](https://deepwiki.com/nirsimetri/onvif-python)).
- [ ] Add more usage examples for advanced features.
- [ ] Add benchmarking and performance metrics.
- [ ] Add community-contributed device configuration templates.

## Related Projects

- [onvif-products-directory](https://github.com/nirsimetri/onvif-products-directory):
	This project is a comprehensive ONVIF data aggregation and management suite, designed to help developers explore, analyze, and process ONVIF-compliant product information from hundreds of manufacturers worldwide.

- (soon) [onvif-rest-server](https://github.com/nirsimetri/onvif-rest-server):
	A RESTful API server for ONVIF devices, enabling easy integration of ONVIF device management, media streaming, and other capabilities into web applications and services.

- (soon) [onvif-mcp](https://github.com/nirsimetri/onvif-mcp):
	A Model Context Protocol (MCP) server for ONVIF, providing a unified API and context-based integration for ONVIF devices, clients, and services. It enables advanced automation, orchestration, and interoperability across ONVIF-compliant devices and clients.

## References
- [ONVIF Official Specifications](https://www.onvif.org/profiles/specifications/specification-history/)
- [ONVIF Official Specs Repository](https://github.com/onvif/specs)
- [ONVIF Application Programmer's Guide](https://www.onvif.org/wp-content/uploads/2016/12/ONVIF_WG-APG-Application_Programmers_Guide-1.pdf)
- [ONVIF 2.0 Service Operation Index](https://www.onvif.org/onvif/ver20/util/operationIndex.html)
- [Usage Examples](./examples/)

## Legal Notice

This project is an **independent open-source implementation** of the [ONVIF](https://www.onvif.org) specifications. It is **not affiliated with, endorsed by, or sponsored by ONVIF** or its member companies.

- The name **“ONVIF”** and the ONVIF logo are registered trademarks of the ONVIF organization.  
- Any references to ONVIF within this project are made strictly for the purpose of describing interoperability with ONVIF-compliant devices and services.  
- Use of the ONVIF trademark in this repository is solely nominative and does not imply any partnership, certification, or official status.
- This project includes WSDL/XSD/HTML files from the official ONVIF specifications.
- These files are © ONVIF and are redistributed here for interoperability purposes.
- The WSDL files in the [`wsdl/`](./onvif/wsdl) folder are distributed under the ONVIF Contributor License Agreement and Apache License 2.0. See [`LICENSE.md`](./onvif/wsdl/LICENSE.md) for details.
- All rights to the ONVIF specifications are reserved by ONVIF.

If you require certified ONVIF-compliant devices or clients, please refer to the official [ONVIF conformant product list](https://www.onvif.org/conformant-products/). For authoritative reference and the latest official ONVIF specifications, please consult the [ONVIF Official Specifications](https://www.onvif.org/profiles/specifications/specification-history/).

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE.md) for details.