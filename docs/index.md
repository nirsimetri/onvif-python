# ONVIF Python

[![Python Version](https://img.shields.io/pypi/pyversions/onvif-python?logo=python&logoColor=white&color=blue&style=plastic&label=Python)](https://pypi.org/project/onvif-python){ .no-external-icon }
[![PyPI Version](https://img.shields.io/pypi/v/onvif-python?logo=pypi&logoColor=white&color=blue&style=plastic&label=PyPI)](https://pypi.org/project/onvif-python/){ .no-external-icon }
[![Quality](https://img.shields.io/codacy/grade/bff08a94e4d447b690cea49c6594826d?style=plastic&logo=codacy&label=Quality)](https://app.codacy.com/gh/nirsimetri/onvif-python/dashboard){ .no-external-icon }
[![Coverage](https://img.shields.io/codacy/coverage/bff08a94e4d447b690cea49c6594826d?style=plastic&logo=codacy&label=Coverage)](https://app.codacy.com/gh/nirsimetri/onvif-python/coverage){ .no-external-icon }
[![Downloads](https://img.shields.io/pepy/dt/onvif-python?label=Downloads&color=red&style=plastic)](https://pepy.tech/projects/onvif-python){ .no-external-icon }
<br>
[![Build](https://img.shields.io/github/actions/workflow/status/nirsimetri/onvif-python/python-app.yml?logo=github&style=plastic&label=Build)](https://github.com/nirsimetri/onvif-python/actions/workflows/python-app.yml){ .no-external-icon }
[![Upload Python](https://img.shields.io/github/actions/workflow/status/nirsimetri/onvif-python/python-publish.yml?logo=github&style=plastic&label=Upload%20Package)](https://github.com/nirsimetri/onvif-python/actions/workflows/python-publish.yml){ .no-external-icon }
[![CLI Cross-Platform](https://img.shields.io/github/actions/workflow/status/nirsimetri/onvif-python/cli-cross-platform.yml?logo=github&style=plastic&label=CLI%20Cross-Platform)](https://github.com/nirsimetri/onvif-python/actions/workflows/cli-cross-platform.yml){ .no-external-icon }


**[ONVIF](https://www.onvif.org) (Open Network Video Interface Forum)** is a global standard for the interface of IP-based physical security products, including network cameras, video recorders, and related systems.  

Behind the scenes, ONVIF communication relies on **[SOAP](https://en.wikipedia.org/wiki/SOAP) (Simple Object Access Protocol)**; an [XML](https://en.wikipedia.org/wiki/XML)-based messaging protocol with strict schema definitions ([WSDL](https://en.wikipedia.org/wiki/Web_Services_Description_Language) and [XSD](https://en.wikipedia.org/wiki/XML_Schema_(W3C))). SOAP ensures interoperability, but when used directly it can be verbose, complex, and error-prone.  

This library simplifies that process by wrapping SOAP communication into a clean, Pythonic API. You no longer need to handle low-level XML parsing, namespaces, or security tokens manually; the library takes care of it, letting you focus on building functionality.

## Who Is It For?
- **Individual developers** exploring ONVIF or building hobby projects  
- **Companies** building video intelligence, analytics, or VMS platforms  
- **Security integrators** who need reliable ONVIF interoperability across devices

## Requirements

- **Python**: 3.10 or higher
- **Dependencies**:
    - [`zeep>=4.3.0`](https://github.com/mvantellingen/python-zeep) - SOAP client for ONVIF communication
    - [`requests>=2.32.0`](https://github.com/psf/requests) - HTTP library for network requests
