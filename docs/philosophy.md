!!! info
    This library will be continuously updated as ONVIF versions are updated. It uses a built-in WSDL that will always follow changes to the [ONVIF WSDL Specifications](https://github.com/onvif/specs). You can also use your own ONVIF WSDL file by adding the `wsdl_dir` argument; see [ONVIFClient](core/onvif_client.md).

### WYSIWYG (What You See is What You Get)
Every ONVIF operation in the library mirrors the official ONVIF specification exactly. Method names, parameter structures, and response formats follow ONVIF standards without abstraction layers or renamed interfaces. What you see in the ONVIF documentation is exactly what you get in Python.

### Device Variety Interoperability
Built to handle the real-world diversity of ONVIF implementations across manufacturers. The library gracefully handles missing features, optional operations, and vendor-specific behaviors through comprehensive error handling and fallback mechanisms. Whether you're working with high-end enterprise cameras or budget IP cameras, the library adapts.

### Official Specifications Accuracy
All service implementations are generated and validated against official `ONVIF WSDL Specifications`. The library includes comprehensive test suites that verify compliance with ONVIF standards, ensuring that method signatures, parameter types, and behavior match the official specifications precisely.

### Modern Python Approach
Designed for excellent IDE support with full type hints, auto-completion, and immediate error detection. You'll get `TypeError` exceptions upfront when accessing ONVIF operations with wrong arguments, instead of cryptic `SOAP faults` later. Clean, Pythonic API that feels natural to Python developers while maintaining ONVIF compatibility.

### Minimal Dependencies
Only depends on essential, well-maintained libraries (`zeep` for SOAP, `requests` for HTTP). No bloated framework dependencies or custom XML parsers. The library stays lightweight while providing full ONVIF functionality, making it easy to integrate into any project without dependency conflicts.