---
hide:
  - path
comments: true
---

!!! info
    This library will be continuously updated as ONVIF versions are updated. It uses a built-in WSDL that will always follow changes to the [ONVIF WSDL Specifications](https://github.com/onvif/specs).
    
    You can also use your own ONVIF WSDL file by adding the `wsdl_dir` argument; see [`ONVIFClient`](main/onvif_client.md).

### WYSIWYG (What You See is What You Get)
Every ONVIF operation in the library mirrors the official ONVIF specification exactly. Method names, parameter structures, and response formats follow ONVIF standards without abstraction layers or renamed interfaces. What you see in the ONVIF documentation is exactly what you get in Python.

### Device Variety Interoperability
Built to handle the real-world diversity of ONVIF implementations across manufacturers. If a camera does not support a given ONVIF operation, the library returns `None` rather than raising a SOAP fault, so your code keeps running without `try`/`except` blocks around every call. Whether you're working with high-end enterprise cameras or budget IP cameras, the library adapts.

### Official Specifications Accuracy
All service implementations are generated and validated against official `ONVIF WSDL Specifications`. The library includes comprehensive test suites that verify compliance with ONVIF standards, ensuring that method signatures, parameter types, and behavior match the official specifications precisely.

### Modern Python Approach
Designed for excellent IDE support with full type hints, docstrings, auto-completion, and immediate error detection. You'll get `TypeError` exceptions upfront when accessing ONVIF operations with wrong arguments, instead of cryptic `SOAP faults` later. You call `client.media().GetSnapshotUri()` and get a URL back. No XML parsing, no WSDL files, no manually constructed SOAP envelopes.

### Minimal Dependencies
Only depends on essential, well-maintained libraries ([`zeep`](https://github.com/mvantellingen/python-zeep) for SOAP, [`requests`](https://github.com/psf/requests) for HTTP). No bloated framework dependencies. The library stays lightweight while providing full ONVIF functionality, making it easy to integrate into any project without dependency conflicts.