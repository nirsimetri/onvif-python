![Windows](https://img.shields.io/badge/Windows-0078D6?style=plastic&logo=gitforwindows&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-FCC624?style=plastic&logo=linux&logoColor=black)
![macOS](https://img.shields.io/badge/macOS-1A9FEE?style=plastic&logo=apple&logoColor=black)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-A22846?style=plastic&logo=raspberrypi&logoColor=black)

This library includes a powerful command-line interface (CLI) for interacting with ONVIF devices directly from your terminal. It supports both direct command execution and an interactive shell mode, providing a flexible and efficient way to manage and debug ONVIF devices.

!!! info
    The CLI is automatically installed when you install the `onvif-python` see [Installation](../installation.md). This feature has been available since `onvif-python` version [`>=0.1.1`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.1).

## Features

- **Device Discovery:** Automatic ONVIF device discovery on local network using WS-Discovery protocol.
- **Interactive Shell:** A user-friendly shell with tab completion, command history, and colorized output.
- **Direct Command Execution:** Run ONVIF commands directly from the terminal for scripting and automation.
- **Services Discovery:** Automatically detects available services on the device.
- **Connection Management:** Supports HTTP/HTTPS, custom timeouts, and SSL verification.
- **Data Management:** Store results from commands and use them as parameters in subsequent commands.
- **Cross-Platform:** Works on Windows, macOS, Linux, and Raspberry Pi.

## Screenshoot

<table>
  <tr>
    <td width="35%">
      <a href="https://github.com/nirsimetri/onvif-python">
        <img src="https://raw.githubusercontent.com/nirsimetri/onvif-python/refs/heads/main/assets/images/onvif_cli.png" />
      </a>
    </td>
    <td width="65%">
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

## Help Command

<details>
<summary><b>Direct CLI</b></summary> 

```bash
usage: onvif [-h] [--host HOST] [--port PORT] [--username USERNAME] [--password PASSWORD] [--discover] [--filter FILTER] [--interface INTERFACE] [--discovery-timeout DISCOVERY_TIMEOUT] [--search SEARCH]
             [--page PAGE] [--per-page PER_PAGE] [--timeout TIMEOUT] [--https] [--no-verify] [--no-patch] [--interactive] [--debug] [--wsdl WSDL] [--cache {all,db,mem,none}]
             [--health-check-interval HEALTH_CHECK_INTERVAL] [--output OUTPUT] [--version]
             [service] [method] [params ...]

ONVIF Terminal Client — v0.3.0
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
  --interface INTERFACE, -if INTERFACE
                        Specify network interface IP for discovery (default: auto-detect)
  --discovery-timeout DISCOVERY_TIMEOUT, -dt DISCOVERY_TIMEOUT
                        Discovery timeout in seconds (default: 4)
  --search SEARCH, -s SEARCH
                        Search ONVIF products database by model or company (e.g., 'c210', 'hikvision')
  --page PAGE           Page number for search results (default: 1)
  --per-page PER_PAGE   Number of results per page (default: 20)
  --timeout TIMEOUT     ONVIF connection timeout in seconds (default: 10)
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
                        Save command output to file. Supports .json, .xml extensions for format detection, or plain text. XML format automatically enables debug mode for SOAP capture.
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
<summary><b>Interactive Shell</b></summary> 

```bash
ONVIF Interactive Shell — v0.3.0
https://github.com/nirsimetri/onvif-python

Basic Commands:
  capabilities, caps       - Show device capabilities
  services                 - Show available services with details
  info                     - Show connection and device information
  exit                     - Exit the shell
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

## Usage

### Interactive Mode

The interactive shell is recommended for exploration and debugging. It provides an intuitive way to navigate services, call methods, and view results.

To start the interactive shell, provide the connection details:

```bash
onvif --host 192.168.1.17 --port 8000 --username admin --password admin123 -i
```

If you omit the username or password, you will be prompted to enter them securely.

#### Interactive Shell Commands

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
| `exit` | Exit the shell |

!!! warning
    You can see all the other commands available in the interactive shell by trying it out directly. The interactive shell runs periodic background health checks to detect connection loss. It uses silent TCP pings to avoid interrupting your work and will automatically exit if the device is unreachable, similar to an SSH session.

#### Command Chaining with `&&`

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

### Device Discovery (WS-Discovery)

The CLI includes automatic ONVIF device discovery using the WS-Discovery protocol. This feature allows you to find all ONVIF-compliant devices on your local network without knowing their IP addresses beforehand (applied at [`>=v0.1.2`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.1.2)).

!!! danger
    - Discovery only works on the local network (same subnet)
    - Some networks may block multicast traffic (check firewall settings)
    - The `--host` and `--port` arguments are not required when using `--discover`
    - You can still provide `--username` and `--password` upfront to avoid prompts

#### Discover and Connect Interactively
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

#### Discover and Execute Command
```bash
# Discover devices and execute a command on the selected device
onvif media GetProfiles --discover --username admin --password admin123

# Short form
onvif media GetProfiles -d -u admin -p admin123
```

#### How Device Discovery Works

1. **Automatic Network Scanning**: Sends a WS-Discovery Probe message to the multicast address `239.255.255.250:3702`
2. **Device Detection**: Listens for ProbeMatch responses from ONVIF devices (default timeout: 4 seconds)
3. **Interactive Selection**: Displays a numbered list of discovered devices with their details:
   - Device UUID (Endpoint Reference)
   - XAddrs (ONVIF service URLs)
   - Device Types (e.g., NetworkVideoTransmitter)
   - Scopes (name, location, hardware, profile information)
4. **Connection**: Once you select a device, the CLI automatically connects using the discovered host and port

#### Example Discovery Output
```bash
Discovering ONVIF devices on network...
Network interface: 192.168.1.100
Timeout: 4s

Found 2 ONVIF device(s):

[1] 192.168.1.14:2020
    [id] 3fa1fe68-b915-4053-a3e1-a8294833fe3c
    [xaddrs] [http://192.168.1.14:2020/onvif/device_service]
    [types] [tdn:NetworkVideoTransmitter]
    [scopes] [name/C210] [hardware/C210] [Profile/S] [location/Hong Kong]

[2] 192.168.1.17:8000
    [id] 7d04ff31-61e6-11f0-a00c-6056eef47207
    [xaddrs] [http://192.168.1.17:8000/onvif/device_service]
    [types] [dn:NetworkVideoTransmitter] [tds:Device]
    [scopes] [type/NetworkVideoTransmitter] [name/IPC_123465959]

Select device number 1-2 or q to quit: 1

Selected: 192.168.1.14:2020
```

### Direct Command Execution

You can also execute a single ONVIF command directly. This is useful for scripting or quick checks.

#### Syntax
```bash
onvif <service> <method> [parameters...] -H <host> -P <port> -u <user> -p <pass>
```

#### Example
```bash
# Get device capabilities
onvif devicemgmt GetCapabilities Category=All -H 192.168.1.17 -P 8000 -u admin -p admin123

# Move a PTZ camera
onvif ptz ContinuousMove ProfileToken=Profile_1 Velocity='{"PanTilt": {"x": 0.1, "y": 0}}' -H 192.168.1.17 -P 8000 -u admin -p admin123

# Save output to file
onvif devicemgmt GetDeviceInformation --host 192.168.1.17 --port 8000 --username admin --password admin123 --output device_info.json
onvif media GetProfiles -H 192.168.1.17 -P 8000 -u admin -p admin123 -o profiles.xml
```

### ONVIF Product Search

The CLI includes a built-in database of ONVIF-compatible products that can be searched to help identify and research devices before connecting (applied at [`>=v0.2.0`](https://github.com/nirsimetri/onvif-python/releases/tag/v0.2.0)).

#### Basic Search
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

#### Paginated Results
```bash
# Navigate through multiple pages of results
onvif --search "hikvision" --page 2 --per-page 5
onvif -s "axis" --page 1 --per-page 10

# Adjust results per page (1-100)
onvif --search "camera" --per-page 20
```

#### Search Database Information

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

#### Example Output
```bash
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

All [`ONVIFClient`](../api/cores/onvif_client.md) parameters (like `--timeout`, `--https`, `--cache`, etc.) are available as command-line arguments.

Use `onvif --help` to see all available options.