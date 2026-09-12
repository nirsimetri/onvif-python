<h1 align="center">ONVIF Python</h1>

<div align="center">
<a href="https://app.codacy.com/gh/nirsimetri/onvif-python/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade"><img src="https://img.shields.io/codacy/grade/bff08a94e4d447b690cea49c6594826d?style=plastic&logo=codacy&label=Code%20Quality"/></a>
<a href="https://pypi.org/project/onvif-python/"><img alt="PyPI Version" src="https://img.shields.io/badge/Version-0.3.1-orange?logo=python&logoColor=white&color=yellow&style=plastic"></a>
<a href="https://pepy.tech/projects/onvif-python"><img alt="Pepy Total Downloads" src="https://img.shields.io/pepy/dt/onvif-python?logo=pypi&logoColor=white&label=Downloads&color=red&style=plastic"></a>
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

Behind the scenes, ONVIF communication relies on **[SOAP](https://en.wikipedia.org/wiki/SOAP) (Simple Object Access Protocol)**; an [XML](https://en.wikipedia.org/wiki/XML)-based messaging protocol with strict schema definitions ([WSDL](https://en.wikipedia.org/wiki/Web_Services_Description_Language)/[XSD](https://en.wikipedia.org/wiki/XML_Schema_(W3C))). SOAP ensures interoperability, but when used directly it can be verbose, complex, and error-prone.  

This library simplifies that process by wrapping SOAP communication into a clean, Pythonic API. You no longer need to handle low-level XML parsing, namespaces, or security tokens manually; the library takes care of it, letting you focus on building functionality.

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
```shell
pip install --upgrade onvif-python
```

Or clone this repository and install locally:
```shell
git clone https://github.com/nirsimetri/onvif-python
cd onvif-python
pip install .
```

Once the installation is successful, you can also immediately access the [ONVIF CLI](https://nirsimetri.github.io/onvif-python/core/onvif_cli/) via the terminal using:
```shell
onvif --version
```

## Documentation

For complete guide, including usage examples and API references, please visit the [Documentation Page](https://nirsimetri.github.io/onvif-python/).

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE.md) for details.