---
hide:
  - path
comments: true
---

This documentation uses a consistent set of badges to identify version requirements, implementation details, feature availability, parameter constraints, and related resources.

Each badge conveys a specific meaning, helping readers quickly understand the compatibility, behavior, or purpose of a component or operation. Refer to the conventions below for the meaning of each badge and the information it communicates.

## Version requirements

### <!-- md:version 0.0 --> → Package version { data-toc-label="Package version" }

Indicates the minimum `onvif-python` package version required to use a feature, parameter, class, or operation. The badge links to the corresponding release documentation.

### <!-- md:onvif_version 0.0 https://www.onvif.org/profiles/specifications/specification-history --> → ONVIF version { data-toc-label="ONVIF version" }

Indicates the minimum ONVIF version required for device compatibility. The badge links to the relevant ONVIF specification.

## Implementation details

### <!-- md:internal --> → Internal { data-toc-label="Internal" }

Identifies an internal implementation detail that is not intended for direct public use.

Internal components may change without following the same compatibility guarantees as the public API.

### <!-- md:entry_point --> → Entry point { data-toc-label="Entry point" }

Identifies the entry point of an ONVIF service or operation, helping readers locate where a particular interaction begins.

### <!-- md:exception --> → Exception { data-toc-label="Exception" }

Identifies an exception type associated with an operation, indicating the kind of error that may be raised.

### <!-- md:error_handler --> → Error handler { data-toc-label="Error handler" }

Identifies a function or mechanism responsible for handling errors during an operation.

## Features and extensions

### <!-- md:plugin --> → Plugin { data-toc-label="Plugin" }

A [Zeep plugin](https://docs.python-zeep.org/en/master/plugins.html) that intercepts and processes SOAP messages exchanged by the client.

### <!-- md:utility --> → Utility { data-toc-label="Utility" }

Identifies a supporting utility that provides reusable functionality for common tasks.

### <!-- md:feature --> → Feature { data-toc-label="Feature" }

Indicates an optional feature that provides additional functionality or behavior. Availability may depend on configuration, device capabilities, or the operation being performed.

### <!-- md:flag experimental --> → Experimental { data-toc-label="Experimental" }

Marks a feature that is experimental and may undergo changes in behavior, implementation, or API before becoming stable.

## Examples and references

### <!-- md:example_view get_snapshot.py type=default --> → Example view { data-toc-label="Example view" }

Links directly to the example source code for inspection.

### <!-- md:example_file logger.py type=default --> → Example file { data-toc-label="Example file" }

Links to the example file so readers can inspect or download it.

### <!-- md:module client.py type=default --> → Module { data-toc-label="Module" }

Links to the corresponding Python module in the repository, allowing readers to inspect its implementation.

### <!-- md:demo https://github.com/nirsimetri/onvif-python/tree/main/examples type=default --> → Demo { data-toc-label="Demo" }

Links to an external repository containing a demonstration or related implementation.

## Parameters and properties

### <!-- md:default --> → Default value { data-toc-label="Default value" }

Displays the default value of a parameter, setting, or property when no explicit value is provided.

#### <!-- md:default none --> → Empty default { data-toc-label="Empty default" }

Indicates that the default value is `None`, meaning no value is assigned by default.

#### <!-- md:default computed --> → Computed default { data-toc-label="Computed default" }

Indicates that the default value is computed dynamically at runtime rather than being a fixed, explicitly defined value.

### <!-- md:flag required --> → Required { data-toc-label="Required" }

Indicates that a parameter, value, or property is required for the relevant operation or configuration.

### <!-- md:flag metadata --> → Metadata { data-toc-label="Metadata" }

Identifies a property that provides metadata about a component, object, or resource.