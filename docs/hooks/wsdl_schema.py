"""Attach generated WSDL schemas to API operations."""

import json
from pathlib import Path
from typing import Any

from griffe import Extension, Function

from onvif.mappings import ONVIF_NAMESPACE_MAP

# Keys are normalized Python API service identifiers.
# Values are paths relative to metadata_dir.
PREFERRED_SOURCES: dict[str, str] = {
    "display": "ver10/display.json",
    "events": "ver10/events/wsdl/event-vs.json",
    "pullpoint": "ver10/events/wsdl/event-vs.json",
    "notification": "ver10/events/wsdl/bw-2-vs-mod.json",
    "subscription": "ver10/events/wsdl/bw-2-vs-mod.json",
    "pausable_subscription": "ver10/events/wsdl/bw-2-vs-mod.json",
}


class WSDLSchemaExtension(Extension):
    """Load WSDL metadata and attach schemas to matching API operations."""

    def __init__(
        self,
        metadata_dir: str = "docs/generated/wsdl",
    ) -> None:
        super().__init__()
        self.metadata_dir = Path(metadata_dir)
        self.schemas: list[dict[str, Any]] = []
        self._load_metadata()

    @staticmethod
    def _normalize(value: str) -> str:
        """Normalize an identifier for case-insensitive comparison."""
        return "".join(char for char in value.lower() if char.isalnum())

    @classmethod
    def _path_components(cls, value: str) -> set[str]:
        """Extract normalized identifiers from a dotted Python path."""
        return {
            normalized
            for component in value.split(".")
            if (normalized := cls._normalize(component))
        }

    @classmethod
    def _namespace_services(
        cls,
        namespace: str,
    ) -> tuple[tuple[str, str], ...]:
        """Return service identifiers and bindings for a WSDL namespace."""
        normalized_namespace = namespace.rstrip("/").lower()

        for mapped_namespace, services in ONVIF_NAMESPACE_MAP.items():
            if mapped_namespace.rstrip("/").lower() == normalized_namespace:
                return services

        return ()

    def _load_metadata(self) -> None:
        """Load operation metadata while preserving WSDL context."""
        if not self.metadata_dir.is_dir():
            return

        for path in sorted(self.metadata_dir.rglob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue

            if not isinstance(data, dict):
                continue

            namespace = data.get("target_namespace")
            operations = data.get("operations")

            if not isinstance(namespace, str) or not isinstance(operations, list):
                continue

            binding = data.get("binding")

            for operation in operations:
                if not isinstance(operation, dict):
                    continue

                name = operation.get("name")
                if not isinstance(name, str) or not name:
                    continue

                self.schemas.append(
                    {
                        "target_namespace": namespace,
                        "source": path,
                        "binding": binding,
                        "operation": operation,
                    }
                )

    @classmethod
    def _mapped_service(
        cls,
        record: dict[str, Any],
    ) -> str | None:
        """Resolve the Python service identifier from namespace and binding."""
        namespace = record["target_namespace"]
        operation = record["operation"]
        services = cls._namespace_services(namespace)

        if not services:
            services = tuple(
                (service, mapped_binding)
                for mapped_services in ONVIF_NAMESPACE_MAP.values()
                for service, mapped_binding in mapped_services
            )

        binding = operation.get("binding") or record.get("binding")
        bindings = operation.get("bindings", [])

        if binding:
            bindings = [binding]
        elif not bindings:
            bindings = [
                operation.get("binding_name"),
                record.get("service_binding"),
            ]
            bindings = [item for item in bindings if item]

        if not bindings:
            return None

        normalized_bindings = {
            cls._normalize(item) for item in bindings if isinstance(item, str) and item
        }

        matches = {
            cls._normalize(service)
            for service, mapped_binding in services
            if cls._normalize(mapped_binding) in normalized_bindings
        }

        if len(matches) != 1:
            return None

        return matches.pop()

    def _preferred_source(
        self,
        service: str,
    ) -> str | None:
        """Return the preferred metadata source for a Python API service."""
        normalized_service = self._normalize(service)

        for identifier, source in PREFERRED_SOURCES.items():
            if self._normalize(identifier) == normalized_service:
                return source

        return None

    def _select_candidate(
        self,
        candidates: list[dict[str, Any]],
        service: str,
        func_path: str,
    ) -> dict[str, Any] | None:
        """Select a unique candidate, preferring its configured source."""
        if len(candidates) == 1:
            return candidates[0]

        preferred_source = self._preferred_source(service)

        if preferred_source is None:
            print(
                f"[WSDL] Ambiguous match: {func_path} "
                f"({len(candidates)} candidates)"
            )
            return None

        preferred_path = (self.metadata_dir / preferred_source).resolve()
        preferred_candidates = [
            record
            for record in candidates
            if record["source"].resolve() == preferred_path
        ]

        if len(preferred_candidates) == 1:
            return preferred_candidates[0]

        print(
            f"[WSDL] Ambiguous match: {func_path} "
            f"({len(candidates)} candidates; "
            f"preferred source={preferred_source!r}, "
            f"matches={len(preferred_candidates)})"
        )
        return None

    def on_function(self, *, func: Function, **kwargs: Any) -> None:
        """Attach schema metadata when exactly one operation matches."""
        function_components = self._path_components(func.path)

        candidates = [
            record
            for record in self.schemas
            if record["operation"].get("name") == func.name
            and (service := self._mapped_service(record)) is not None
            and service in function_components
        ]

        if not candidates:
            return

        # The matching Python service is derived from the candidate records.
        services = {
            service
            for record in candidates
            if (service := self._mapped_service(record)) is not None
        }

        if len(services) != 1:
            print(
                f"[WSDL] Ambiguous service: {func.path} "
                f"({', '.join(sorted(services))})"
            )
            return

        service = services.pop()
        selected = self._select_candidate(candidates, service, func.path)

        if selected is not None:
            func.extra["wsdl_schema"] = selected["operation"]
