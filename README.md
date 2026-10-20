# ONVIF Python [![Downloads](https://img.shields.io/pypi/dm/onvif-python?label=Downloads&style=plastic)](https://pepy.tech/projects/onvif-python)

[![Python Version](https://img.shields.io/pypi/pyversions/onvif-python?logo=python&logoColor=white&color=blue&style=plastic&label=Python)](https://pypi.org/project/onvif-python)
[![PyPI Version](https://img.shields.io/pypi/v/onvif-python?logo=pypi&logoColor=white&color=blue&style=plastic&label=PyPI)](https://pypi.org/project/onvif-python/)
[![Quality](https://img.shields.io/codacy/grade/bff08a94e4d447b690cea49c6594826d?style=plastic&logo=codacy&label=Quality)](https://app.codacy.com/gh/nirsimetri/onvif-python/dashboard)
[![Coverage](https://img.shields.io/codacy/coverage/bff08a94e4d447b690cea49c6594826d?style=plastic&logo=codacy&label=Coverage)](https://app.codacy.com/gh/nirsimetri/onvif-python/coverage)
<br>
[![Build](https://img.shields.io/github/actions/workflow/status/nirsimetri/onvif-python/python-app.yml?logo=github&style=plastic&label=Build)](https://github.com/nirsimetri/onvif-python/actions/workflows/python-app.yml)
[![Upload Python](https://img.shields.io/github/actions/workflow/status/nirsimetri/onvif-python/python-publish.yml?logo=github&style=plastic&label=Upload%20Package)](https://github.com/nirsimetri/onvif-python/actions/workflows/python-publish.yml)
[![CLI Cross-Platform](https://img.shields.io/github/actions/workflow/status/nirsimetri/onvif-python/cli-cross-platform.yml?logo=github&style=plastic&label=CLI%20Cross-Platform)](https://github.com/nirsimetri/onvif-python/actions/workflows/cli-cross-platform.yml)


**[ONVIF](https://www.onvif.org) (Open Network Video Interface Forum)** is a global standard for the interface of IP-based physical security products, including network cameras, video recorders, and related systems.  

Behind the scenes, ONVIF communication relies on **[SOAP](https://en.wikipedia.org/wiki/SOAP) (Simple Object Access Protocol)**; an [XML](https://en.wikipedia.org/wiki/XML)-based messaging protocol with strict schema definitions ([WSDL](https://en.wikipedia.org/wiki/Web_Services_Description_Language)/[XSD](https://en.wikipedia.org/wiki/XML_Schema_(W3C))). SOAP ensures interoperability, but when used directly it can be verbose, complex, and error-prone.  

This library simplifies that process by wrapping SOAP communication into a clean, Pythonic API. You no longer need to handle low-level XML parsing, namespaces, or security tokens manually; the library takes care of it, letting you focus on building functionality.

## Who Is It For?

<table>
  <tr>
    <th align="start">
    <img
      src="https://raw.githubusercontent.com/Templarian/MaterialDesign/refs/heads/master/svg/account-hard-hat.svg"
      width="24"
      height="24"
      valign="middle"
    />&nbsp;Individual Developers
    </th>
    <th align="start">
    <img
      src="https://raw.githubusercontent.com/Templarian/MaterialDesign/refs/heads/master/svg/video-wireless.svg"
      width="24"
      height="24"
      valign="middle"
    />&nbsp;Platform Developers
    </th>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <p>Explore ONVIF capabilities and build applications for IP cameras and compatible devices.</p>
    </td>
    <td width="50%" valign="top">
      <p>Build video intelligence, analytics, and video management system (VMS) platforms.</p>
    </td>
  </tr>
  <tr>
    <th align="start">
    <img
      src="https://raw.githubusercontent.com/Templarian/MaterialDesign/refs/heads/master/svg/cctv.svg"
      width="24"
      height="24"
      valign="middle"
    />&nbsp;Security Integrators
    </th>
    <th align="start">
    <img
      src="https://raw.githubusercontent.com/Templarian/MaterialDesign/refs/heads/master/svg/chip.svg"
      width="24"
      height="24"
      valign="middle"
    />&nbsp;Device & IoT Engineers
    </th>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <p>Integrate security devices and troubleshoot ONVIF interoperability across vendors.</p>
    </td>
    <td width="50%" valign="top">
      <p>Develop, test, and integrate ONVIF-compliant devices and IP-based physical security systems.</p>
    </td>
  </tr>
</table>

## Requirements

Python **3.10 or higher** is required.

## Dependencies

- [zeep](https://github.com/mvantellingen/python-zeep) → SOAP client for ONVIF communication.
- [requests](https://github.com/psf/requests) → HTTP library for network requests.
- [pyreadline3](https://github.com/pyreadline3/pyreadline3) → Only installed on Windows (`win32`) for CLI auto-completion.

## Installation

From official [PyPI](https://pypi.org/project/onvif-python/):
```shell
pip install --upgrade onvif-python
```

Or install using [pipx](https://pipx.pypa.io/stable/) for an isolated environment:
```shell
pipx install git+https://github.com/nirsimetri/onvif-python

```

Or clone this repository and install locally:
```shell
git clone https://github.com/nirsimetri/onvif-python
cd onvif-python
pip install .
```

Once the installation is successful, you can also immediately access the [ONVIF CLI](https://onvif-python.pages.dev/main/onvif_cli/) via the terminal using:
```shell
onvif --help
```

## Prebuilt Binaries (No Python Required)

To use the [ONVIF CLI](https://onvif-python.pages.dev/main/onvif_cli/) without installing Python or additional dependencies, download a prebuilt binary for your platform from the [GitHub Releases](https://github.com/nirsimetri/onvif-python/releases) page.

Each release includes downloadable binary assets for supported platforms and architectures. Choose the appropriate binary from the table below:

| Platform | Architecture | Download |
|---|---|---|
| <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/refs/heads/master/svgs/brands/linux.svg" width="20" height="20" valign="middle"/> &nbsp;Linux | AMD64 (64-bit) | [onvif-linux-amd64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-linux-amd64.zip) |
| <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/refs/heads/master/svgs/brands/linux.svg" width="20" height="20" valign="middle"/> &nbsp;Linux | i386 (32-bit) | [onvif-linux-i386.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-linux-i386.zip) |
| <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/refs/heads/master/svgs/brands/linux.svg" width="20" height="20" valign="middle"/> &nbsp;Linux | ARM64 (aarch64) | [onvif-linux-arm64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-linux-arm64.zip) |
| <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/refs/heads/master/svgs/brands/windows.svg" width="20" height="20" valign="middle"/> &nbsp;Windows | x64 (64-bit) | [onvif-windows-win64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-windows-win64.zip) |
| <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/refs/heads/master/svgs/brands/windows.svg" width="20" height="20" valign="middle"/> &nbsp;Windows | x86 (32-bit) | [onvif-windows-win32.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-windows-win32.zip) |
| <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/refs/heads/master/svgs/brands/windows.svg" width="20" height="20" valign="middle"/> &nbsp;Windows | ARM64 | [onvif-windows-arm64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-windows-arm64.zip) |
| <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/refs/heads/master/svgs/brands/apple.svg" width="20" height="20" valign="middle"/> &nbsp;macOS | Intel (AMD64) | [onvif-macos-amd64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-macos-amd64.zip) |
| <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/refs/heads/master/svgs/brands/apple.svg" width="20" height="20" valign="middle"/> &nbsp;macOS | Apple Silicon (ARM64) | [onvif-macos-arm64.zip](https://github.com/nirsimetri/onvif-python/releases/latest/download/onvif-macos-arm64.zip) |

## Documentation

For complete guide, including usage examples and API references, please visit the [Documentation Site](https://onvif-python.pages.dev/).

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
