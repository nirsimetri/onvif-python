---
hide:
  - navigation
---

# ONVIF Python &nbsp;[![Downloads](https://img.shields.io/pepy/dt/onvif-python?label=Downloads&color=red&style=plastic)](https://pepy.tech/projects/onvif-python){ .no-external-icon }


[![Python Version](https://img.shields.io/pypi/pyversions/onvif-python?logo=python&logoColor=white&color=blue&style=plastic&label=Python)](https://pypi.org/project/onvif-python){ .no-external-icon }
[![PyPI Version](https://img.shields.io/pypi/v/onvif-python?logo=pypi&logoColor=white&color=blue&style=plastic&label=PyPI)](https://pypi.org/project/onvif-python/){ .no-external-icon }
[![Quality](https://img.shields.io/codacy/grade/bff08a94e4d447b690cea49c6594826d?style=plastic&logo=codacy&label=Quality)](https://app.codacy.com/gh/nirsimetri/onvif-python/dashboard){ .no-external-icon }
[![Coverage](https://img.shields.io/codacy/coverage/bff08a94e4d447b690cea49c6594826d?style=plastic&logo=codacy&label=Coverage)](https://app.codacy.com/gh/nirsimetri/onvif-python/coverage){ .no-external-icon }
<br>
[![Build](https://img.shields.io/github/actions/workflow/status/nirsimetri/onvif-python/python-app.yml?logo=github&style=plastic&label=Build)](https://github.com/nirsimetri/onvif-python/actions/workflows/python-app.yml){ .no-external-icon }
[![Upload Python](https://img.shields.io/github/actions/workflow/status/nirsimetri/onvif-python/python-publish.yml?logo=github&style=plastic&label=Upload%20Package)](https://github.com/nirsimetri/onvif-python/actions/workflows/python-publish.yml){ .no-external-icon }
[![CLI Cross-Platform](https://img.shields.io/github/actions/workflow/status/nirsimetri/onvif-python/cli-cross-platform.yml?logo=github&style=plastic&label=CLI%20Cross-Platform)](https://github.com/nirsimetri/onvif-python/actions/workflows/cli-cross-platform.yml){ .no-external-icon }


**[ONVIF](https://www.onvif.org) (Open Network Video Interface Forum)** is a global standard for the interface of IP-based physical security products, including network cameras, video recorders, and related systems.  

Behind the scenes, ONVIF communication relies on **[SOAP](https://en.wikipedia.org/wiki/SOAP) (Simple Object Access Protocol)**; an [XML](https://en.wikipedia.org/wiki/XML)-based messaging protocol with strict schema definitions ([WSDL](https://en.wikipedia.org/wiki/Web_Services_Description_Language) and [XSD](https://en.wikipedia.org/wiki/XML_Schema_(W3C))). SOAP ensures interoperability, but when used directly it can be verbose, complex, and error-prone.  

This library simplifies that process by wrapping SOAP communication into a clean, Pythonic API. You no longer need to handle low-level XML parsing, namespaces, or security tokens manually; the library takes care of it, letting you focus on building functionality.

## Who Is It For?

<div class="grid cards" markdown>

-   :material-account-hard-hat:{ .lg .middle }&nbsp; **Individual Developers**

    ---

    Explore ONVIF capabilities, experiment with network cameras, and build hobby projects.

-   :material-corporate-fare:{ .lg .middle }&nbsp; **Companies**

    ---

    Build video intelligence, analytics, and video management system (VMS) platforms.

-   :material-cctv:{ .lg .middle }&nbsp; **Security Integrators**

    ---

    Ensure reliable ONVIF interoperability across cameras and other security devices.

-   :material-chip:{ .lg .middle }&nbsp; **IoT Experts**

    ---

    Test security, assess interoperability, and investigate ONVIF-enabled devices, and related systems.

</div>

## Requirements

<div class="grid cards" markdown>

-   :material-language-python:{ .lg .middle }&nbsp; **Python**

    ---

    Python **3.10 or higher** is required.

-   :material-package-variant-closed:{ .lg .middle }&nbsp; **Zeep**

    ---

    SOAP client for ONVIF communication.

    [<span class="icon-link">:octicons-arrow-right-24: GitHub</span>](https://github.com/mvantellingen/python-zeep){ .no-external-icon }

-   :material-package-variant-closed:{ .lg .middle }&nbsp; **Requests**

    ---

    HTTP library for network requests.

    [<span class="icon-link">:octicons-arrow-right-24: GitHub</span>](https://github.com/psf/requests){ .no-external-icon }

-   :material-package-variant-closed:{ .lg .middle }&nbsp; **Pyreadline3**

    ---

    Only installed on Windows (`win32`).

    [<span class="icon-link">:octicons-arrow-right-24: GitHub</span>](https://github.com/pyreadline3/pyreadline3){ .no-external-icon }

</div>
