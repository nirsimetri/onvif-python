---
hide:
  - path
comments: true
---

<!-- md:version 0.2.0 -->
<!-- md:feature -->
<!-- md:example_file logger.py -->

The `onvif-python` library uses Python's standard [`logging`](https://docs.python.org/3/library/logging.html) module to report diagnostic information about device discovery, WSDL resolution, client operations, and errors. 

!!! note
    You can configure logging through the standard Python logging API without modifying the library.

## Basic Configuration

To enable logging, configure the `onvif` logger before performing ONVIF operations:

```python linenums="1"
import logging

from onvif import ONVIFClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

client = ONVIFClient(
    host="192.168.1.17",
    port=80,
    username="admin",
    password="password",
)

device = client.devicemgmt()
device.GetDeviceInformation()
```

The log output includes the timestamp, logger name, severity level, and message. By default, `logging.basicConfig()` writes logs to the console.

## Logging Levels

Python provides several logging levels to control the amount of diagnostic information:

| Level | Description |
| --- | --- |
| `DEBUG` | Detailed diagnostic information for troubleshooting. |
| `INFO` | General information about application and library operations. |
| `WARNING` | Unexpected conditions that do not necessarily prevent execution. |
| `ERROR` | Errors that prevent an operation from completing successfully. |
| `CRITICAL` | Severe errors that may require immediate attention. |

Use `INFO` for routine execution and `DEBUG` when investigating unexpected behavior.

To enable detailed logging specifically for the library, configure the `onvif` logger:

```python linenums="1"
import logging

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logging.getLogger("onvif").setLevel(logging.DEBUG)
```

This configuration enables detailed ONVIF logs while keeping unrelated application logs at the warning level or above.

## Logging to a File

To persist log output for later inspection, configure a file handler using `logging.basicConfig()`:

```python linenums="1"
import logging

logging.basicConfig(
    filename="onvif.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
)
```

The library's log messages will be written to `onvif.log` instead of the console. This is useful when investigating intermittent connectivity issues or collecting diagnostic information from longer-running applications.

If both console output and file logging are required, configure separate handlers for those destinations.

## SOAP XML Capture

<!-- md:version 0.0.6 -->

Logging diagnostic messages and capturing SOAP XML are separate capabilities.

To inspect the actual SOAP requests and responses exchanged with an ONVIF device, initialize the [`ONVIFClient`](../api/core/onvif_client.md) with `capture_xml=True`:

```python linenums="1"
from onvif import ONVIFClient

client = ONVIFClient(
    host="192.168.1.17",
    port=80,
    username="admin",
    password="password",
    capture_xml=True,
)

device = client.devicemgmt()
device.GetDeviceInformation()

if client.xml_plugin:
    print("Last request:")
    print(client.xml_plugin.get_last_request())

    print("Last response:")
    print(client.xml_plugin.get_last_response())

    print("Captured operations:")
    for item in client.xml_plugin.get_history():
        print(item["operation"], item["type"])
```

When XML capture is enabled, the client's XML capture plugin retains SOAP request and response data for inspection. The captured history can also help identify which operation failed and examine the messages exchanged with the device.

!!! warning "Sensitive Data"
    SOAP messages may contain authentication tokens, device information, network addresses, or other sensitive data. Use XML capture primarily for development and troubleshooting, and avoid exposing captured messages in production logs or public bug reports.

## Filtering Third-Party Logs

The library relies on external components, including Zeep and HTTP-related dependencies. Their diagnostic output can be more verbose than the ONVIF-specific logs you need.

To reduce unrelated output, configure their logger levels independently:

```python linenums="1"
import logging

for name in ("zeep", "urllib3", "requests"):
    logging.getLogger(name).setLevel(logging.WARNING)
```

This suppresses messages below `WARNING` from those logger hierarchies while allowing higher-severity messages through. Adjust the levels when investigating problems originating in a dependency.

## Logging Example

For a complete demonstration, see [`examples/logger.py`](https://github.com/nirsimetri/onvif-python/blob/main/examples/logger.py). It demonstrates console and file logging, configurable severity levels, device discovery, WSDL resolution, client operations, error handling, and optional SOAP XML capture.

Run the example from the repository root:

```console
python examples/logger.py --level DEBUG
```

To specify a device explicitly:

```console
python examples/logger.py 192.168.1.17 admin password --port 80 --level DEBUG
```

Available levels in the example are `DEBUG`, `INFO`, `WARNING`, and `ERROR`. The example creates a timestamped log file in the current working directory.