---
hide:
  - path
---

<style>
  .md-content .md-typeset h1 {
    margin-bottom: 0;
  }
</style>

# Stay tuned and star :star: this repo

[![GitHub stars](https://img.shields.io/github/stars/nirsimetri/onvif-python?style=social&cacheSeconds=3600)](https://github.com/nirsimetri/onvif-python){ .no-external-icon }

!!! info "Release Cycle"
    Starting with [`v0.4.5`](../releases.md/#v0.4.5), this library will follow a **quarterly release cycle**, with regular releases **every 3 months**. Bug fixes, documentation, and security updates may be released outside the regular schedule when necessary.

## Completed
- [x] Add debugging mode with raw XML on SOAP requests and responses ([`v0.0.6`](../releases.md/#v0.0.6))
- [x] Add functionality for `ONVIFClient` to accept a custom `wsdl_dir` ([`v0.1.0`](../releases.md/#v0.1.0))
- [x] Add `ONVIF CLI` program to interact directly with ONVIF devices via terminal ([`v0.1.1`](../releases.md/#v0.1.1))
- [x] Introduce `ONVIFDiscovery` for network device discovery ([`v0.1.6`](../releases.md/#v0.1.6))
- [x] Add comprehensive logging support to the library ([`v0.2.0`](../releases.md/#v0.2.0))
- [x] Add `ONVIFParser` for extracting XML element values from SOAP responses ([`v0.2.2`](../releases.md/#v0.2.2))
- [x] Add support for custom Zeep plugins in `ONVIFClient` initialization ([`v0.2.2`](../releases.md/#v0.2.2))
- [x] Add support for HTTP Digest authentication and optional credentials ([`v0.3.0`](../releases.md/#v0.3.0))
- [x] Add service operation docstrings for IDE assistance and API discoverability ([`v0.3.0`](../releases.md/#v0.3.0))
- [x] Enhance documentation with API references and diagrams (not from [AI Wiki](https://deepwiki.com/nirsimetri/onvif-python)) ([`v0.3.1`](../releases.md/#v0.3.1))
- [x] Add support for renamed and deprecated ONVIF service operations ([`v0.4.3`](../releases.md/#v0.4.3))

## Planned
- [ ] Provide cross-platform standalone CLI binaries via GitHub Actions → (Q4 2026)
- [ ] Add automated comprehensive checks for ONVIF device capabilities → (Q4 2026)
- [ ] Enhance ONVIF product database search results in the CLI → (Q4 2026)
- [ ] Add tutorial blog section to the documentation → (Q4 2026)
- [ ] Add asynchronous (`async`/`await`) support for non-blocking operations → (Q1 2027)
- [ ] Add [ONVIF Client Conformance Testing](https://www.onvif.org/profiles/conformance/client-test/) to the CLI → (Q1 2027)
- [ ] Add benchmarking and performance metrics → (Q1 2027)
- [ ] Implement operation tracking based on the device's ONVIF version → (Q1 2027)
- [ ] Implement structured data models for ONVIF Schemas using [xsdata](https://github.com/tefra/xsdata) → (Q2 2027)
- [ ] Automate operations implementation with official ONVIF specifications → (Q2 2027)
- [ ] Add [ONVIF Device Conformance Testing](https://www.onvif.org/profiles/conformance/device-test-2/) to the CLI → (Q2 2027)