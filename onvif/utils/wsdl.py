"""WSDL file manager for ONVIF services with support for built-in and custom WSDL dir."""

from __future__ import annotations

import logging
import os
from typing import Any

from onvif.mappings import ONVIF_WSDL_MAP, WSDLMap

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ONVIFWSDL:
    """WSDL file manager for ONVIF services.

    This class manages WSDL (Web Services Description Language) file paths, bindings,
    and namespaces for all ONVIF services. It provides a centralized mapping between
    service names and their corresponding WSDL definitions.

    The class supports both built-in WSDLs (bundled with the package) and custom
    WSDL directories for users who want to use their own WSDL files.

    Attributes:
        BASE_DIR (str): Default base directory for WSDL files (Built-in)
        WSDL_MAP (dict[str, dict[str, Any]] | None): Will be initialized when first accessed

    !!! tip "Version History"
        - Available since [`>=v0.1.0`](/onvif-python/releases/#v0.1.0)

    !!! abstract "Features"
        - Centralized WSDL definition mapping for all ONVIF services
        - Support for multiple ONVIF versions (ver10, ver20)
        - Custom WSDL directory support (global and per-call)
        - Automatic path resolution for built-in and custom WSDLs
        - Service discovery with namespace and binding information
        - File existence validation

    !!! warning "WSDL Structure"
        Built-in WSDLs are organized in the ONVIF standard directory structure:

        ```text
        onvif/
        └── wsdl/
            ├── ver10/
            │   └── device/
            │       └── wsdl/
            │           └── devicemgmt.wsdl
            │
            └── ver20/
                ├── media/
                │   └── wsdl/
                │       └── media.wsdl
                └── ptz/
                    └── wsdl/
                        └── ptz.wsdl
        ```

        Custom WSDLs must use a flat structure:

        ```text
        custom/
        └── path/
            ├── devicemgmt.wsdl
            ├── media.wsdl
            └── ptz.wsdl
        ```

    !!! question "Service Definition Format"
        Each service has a definition containing:

        - `filename` : WSDL file name
        - `path`: Full path to WSDL file
        - `binding`: SOAP binding name (e.g., "DeviceBinding")
        - `namespace`: XML namespace URI (e.g., "http://www.onvif.org/ver10/device/wsdl")

    ??? tip "Custom WSDL Directory Priority"
        1. Per-call `custom_wsdl_dir` parameter (highest priority)
        2. Global `_custom_wsdl_dir` setting
        3. Built-in `BASE_DIR` (default)

    ??? note "Notes"
        - All methods are class methods - no need to instantiate
        - WSDL files are lazy-loaded and validated on access
        - Custom WSDL directories use flat file structure
        - Built-in WSDLs follow ONVIF standard directory structure
        - File existence is checked when getting definitions
        - Thread-safe for read operations

    ??? note "See Also"
        - [`ONVIFOperator`](../core/onvif_operator.md): Uses WSDL definitions to create SOAP clients
        - [`ONVIFClient`](../core/onvif_client.md): High-level client that uses this class internally
    """

    # Default base directory for WSDL files (Built-in)
    # Included in the package
    BASE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wsdl")

    # Global custom WSDL directory - can be set once for all services
    _custom_wsdl_dir: str | None = None

    @classmethod
    def set_custom_wsdl_dir(cls, custom_dir: str) -> None:
        """Set global custom WSDL directory for all services.

        !!! tip "Version History"
            - Available since [`>=v0.1.0`](/onvif-python/releases/#v0.1.0)

        Args:
            custom_dir (str): Path to directory containing custom WSDL files

        Example:
            ```python linenums="1"
            from onvif import ONVIFWSDL

            ONVIFWSDL.set_custom_wsdl_dir("/home/user/my_wsdls")
            # All subsequent get_definition calls will use this directory
            ```
        """
        logger.info("Setting custom WSDL directory: %s", custom_dir)
        cls._custom_wsdl_dir = custom_dir

    @classmethod
    def get_custom_wsdl_dir(cls) -> str | None:
        """Get current global custom WSDL directory.

        !!! tip "Version History"
            - Available since [`>=v0.1.0`](/onvif-python/releases/#v0.1.0)

        Returns:
            Current custom WSDL directory, or None if using built-in

        Example:
            ```python linenums="1"
            from onvif import ONVIFWSDL

            ONVIFWSDL.set_custom_wsdl_dir("/custom/path")
            print(ONVIFWSDL.get_custom_wsdl_dir())  # /custom/path
            ```
        """
        return cls._custom_wsdl_dir

    @classmethod
    def clear_custom_wsdl_dir(cls) -> None:
        """Clear custom WSDL directory, revert to built-in WSDLs.

        !!! tip "Version History"
            - Available since [`>=v0.1.0`](/onvif-python/releases/#v0.1.0)

        Example:
            ```python linenums="1"
            from onvif import ONVIFWSDL

            ONVIFWSDL.set_custom_wsdl_dir("/custom/path")
            ONVIFWSDL.clear_custom_wsdl_dir()
            # Now using built-in WSDLs again
            ```
        """
        logger.info("Clearing custom WSDL directory, reverting to built-in WSDLs")
        cls._custom_wsdl_dir = None

    @classmethod
    def _get_base_dir(cls, custom_wsdl_dir: str | None = None) -> str | Any:
        """Get the base WSDL directory, using custom directory if provided.

        This method implements the priority chain for WSDL directory resolution.

        Args:
            custom_wsdl_dir (str | None): Per-call custom directory

        Returns:
            str: Resolved WSDL base directory path

        Priority:
            1. `custom_wsdl_dir` parameter (highest)
            2. `cls._custom_wsdl_dir` global setting
            3. `cls.BASE_DIR` built-in default (lowest)
        """
        # Priority: parameter > global setting > default
        if custom_wsdl_dir:
            return custom_wsdl_dir

        if cls._custom_wsdl_dir:
            return cls._custom_wsdl_dir

        return cls.BASE_DIR

    @classmethod
    def _get_wsdl_map(
        cls, custom_wsdl_dir: str | None = None
    ) -> dict[str, dict[str, Any]] | None:
        """Get WSDL map with proper base directory.

        Generates a complete mapping of all ONVIF services to their WSDL definitions.
        The structure differs based on whether custom WSDLs are used.

        Args:
            custom_wsdl_dir (str | None): Custom WSDL directory path

        Returns:
            dict: Complete WSDL mapping for all services

            WSDL Map Structure:
                {
                    "{service_name}": {
                        "{version}": {
                            "filename": "service.wsdl",
                            "path": "/full/path/to/service.wsdl",
                            "binding": "ServiceBinding",
                            "namespace": "http://www.onvif.org/ver10/service/wsdl"
                        }
                    }
                }

        Path Resolution:
            - Built-in: Uses ONVIF standard directory structure
              Example: ver10/device/wsdl/devicemgmt.wsdl
            - Custom: Uses flat structure with direct filename
              Example: devicemgmt.wsdl
        """
        base_dir = cls._get_base_dir(custom_wsdl_dir)

        use_flat = custom_wsdl_dir is not None or cls._custom_wsdl_dir is not None

        # Default structure for WSDL files
        # If custom_wsdl_dir is provided, use flat structure (direct filename)
        # Otherwise, use the standard ONVIF directory structure
        wsdl_map: WSDLMap = {}

        for service, versions in ONVIF_WSDL_MAP.items():
            wsdl_map[service] = {}

            for version, definition in versions.items():
                filename = definition["filename"]
                relative_path = filename if use_flat else definition["path"]

                wsdl_map[service][version] = {
                    **definition,
                    "path": os.path.join(base_dir, relative_path),
                }

        return wsdl_map

    WSDL_MAP: dict[str, dict[str, Any]] | None = (
        None  # Will be initialized when first accessed
    )

    @classmethod
    def _ensure_wsdl_map_initialized(cls) -> None:
        """Ensure WSDL_MAP is initialized with default values.

        Lazy initialization of the default WSDL map. This is called automatically before
        accessing WSDL_MAP to ensure it's not None.
        """
        if cls.WSDL_MAP is None:
            cls.WSDL_MAP = cls._get_wsdl_map()

    @classmethod
    def get_wsdl_map(cls) -> dict[str, dict[str, Any]]:
        """Get the complete WSDL map for all services.

        !!! tip "Version History"
            - Available since [`>=v0.2.11`](/onvif-python/releases/#v0.2.11)
        """
        cls._ensure_wsdl_map_initialized()

        if cls.WSDL_MAP is None:
            raise RuntimeError("WSDL map was not initialized")

        return cls.WSDL_MAP

    @classmethod
    def get_definition(
        cls, service: str, version: str = "ver10", custom_wsdl_dir=None
    ) -> dict:
        """Get WSDL definition for a specific ONVIF service.

        Returns complete WSDL definition including file path, SOAP binding name,
        and XML namespace for the requested service and version.

        !!! tip "Version History"
            - Available since [`>=v0.1.0`](/onvif-python/releases/#v0.1.0)

        Args:
            service (str): Service name (e.g., "devicemgmt", "media", "ptz").
            version (str): ONVIF version (default: "ver10").
                Common versions: "ver10", "ver20".
            custom_wsdl_dir (str | None): Custom WSDL directory path.
                Overrides global custom directory if provided.

        Returns:
            WSDL definition dictionary.

        !!! abstract "Definition dict"

            | Key | Type | Description |
            | --- | ---- | ----------- |
            | `filename` | `str`  | WSDL file name |
            | `path` | `str | None` | Full path to WSDL file |
            | `binding` | `str` | SOAP binding name |
            | `namespace` | `str` | XML namespace URI |

            !!! tip "Version History"
                - Added in [`>=v0.4.5`](/onvif-python/releases/#v0.4.5): `filename`

        ??? note
            - Most services use ver10, some newer ones use ver20
            - Media has both ver10 (media) and ver20 (media2)
            - Custom WSDLs must match the service name exactly
            - File existence is validated before returning definition
        """
        logger.debug("Getting WSDL definition for service: %s (%s)", service, version)

        # Use custom WSDL map if custom directory is provided
        if custom_wsdl_dir:
            logger.debug("Using custom WSDL directory: %s", custom_wsdl_dir)
            wsdl_map = cls._get_wsdl_map(custom_wsdl_dir)
        else:
            # Ensure default WSDL_MAP is initialized
            cls._ensure_wsdl_map_initialized()
            wsdl_map = cls.WSDL_MAP

        # Safety check for None wsdl_map
        if wsdl_map is None:
            logger.error("Failed to initialize WSDL map")
            raise RuntimeError("Failed to initialize WSDL map")

        if service not in wsdl_map:
            logger.error("Unknown service: %s", service)
            raise ValueError(f"Unknown service: {service}")
        if version not in wsdl_map[service]:
            logger.error("Version %s not available for %s", version, service)
            raise ValueError(f"Version {version} not available for {service}")

        definition = wsdl_map[service][version]
        if not os.path.exists(definition["path"]):
            logger.error("WSDL file not found: %s", definition["path"])
            raise FileNotFoundError(f"WSDL file not found: {definition['path']}")

        logger.debug("WSDL definition resolved: %s", definition["path"])
        return definition
