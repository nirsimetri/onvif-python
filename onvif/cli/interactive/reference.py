"""Reference commands implementation."""

from __future__ import annotations

import json
import re
from typing import Any

from onvif.cli.utils import colorize

from .context import ShellContext


class ReferenceCommands:
    """Provide stored-reference commands."""

    context: ShellContext

    def do_store(self, line) -> None:
        """Store last result with a name: store <name>."""
        if not line:
            print("Usage: store <name>")
            return

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", line):
            print(
                f"{colorize('Error:', 'red')} Invalid name '{line}'. "
                "Only letters, numbers, and underscores allowed, "
                "and must not start with a number."
            )
            return

        if line in self.context.stored_data:
            print(
                f"{colorize('Error:', 'red')} Name '{line}' already exists. "
                "Use a different name or remove it first."
            )
            return

        UNSET = object()  # pylint: disable=invalid-name

        if self.context.last_result is UNSET:
            print(f"{colorize('Error:', 'red')} No result to store")
            return

        self.context.stored_data[line] = self.context.last_result

        metadata = {}

        if self.context.last_service_name:
            metadata["service"] = self.context.last_service_name

        if self.context.last_method:
            metadata["method"] = self.context.last_method

        self.context.stored_metadata[line] = metadata

        service = metadata.get("service", "unknown")
        method = metadata.get("method", "unknown")

        print(
            f"{colorize('Stored result as:', 'green')} "
            f"{colorize('$' + line, 'yellow')} - "
            f"{colorize(service, 'cyan')}.{colorize(method, 'white')}()"
        )

    def do_show(self, line) -> None:
        """Show stored data: show <name> or show <name>.<attribute> or show
        <name>[index]"""
        if not line:
            print(colorize("Stored data:", "green"))
            for name in self.context.stored_data:
                # Get metadata if available
                metadata = self.context.stored_metadata.get(name, {})
                service = metadata.get("service", "unknown")
                method = metadata.get("method", "unknown")

                # Format: name - service.method()
                info = (
                    f"{colorize('$'+name, 'yellow')} - "
                    f"{colorize(service, 'cyan')}.{colorize(method, 'white')}()"
                )
                print(f"  {info}")
            return

        # Parse accessor expression (e.g., profiles[0].token or profiles.Token)
        result = self._resolve_stored_reference(line)
        if result is not None:
            print(str(result))
        else:
            print(f"{colorize('Error:', 'red')} Cannot resolve '{line}'")

    def _substitute_stored_references(self, params_str: str) -> str:
        """Substitute $variable references in parameter string with stored data.

        Args:
            params_str: Parameter string that may contain $variable references

        Returns:
            Parameter string with substituted values
        """
        # Find all $variable references (e.g., $profiles[0].token)
        pattern = (
            r"\$([a-zA-Z_][a-zA-Z0-9_]*(?:\[[0-9]+\])?(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)"
        )

        def replace_reference(match) -> Any | str:
            reference = match.group(1)
            value = self._resolve_stored_reference(reference)

            if value is None:
                print(f"{colorize('Warning:', 'yellow')} Cannot resolve ${reference}")
                return match.group(0)  # Keep original if not found

            # Convert value to string representation suitable for JSON
            # Use json.dumps to serialize values correctly for JSON parsing.
            # This preserves numbers, booleans, nulls, arrays and objects.
            try:
                return json.dumps(value)
            except (TypeError, KeyError, ValueError, RuntimeError):
                # Fall back to string-quoting for anything not serializable
                return json.dumps(str(value))

        return re.sub(pattern, replace_reference, params_str)

    def _resolve_stored_reference(self, reference: str) -> Any | None:
        """Resolve stored data reference like 'profiles[0].token' or 'profiles.Token'.

        Args:
            reference: String reference like 'profiles[0]' or 'profiles.Token'

        Returns:
            Resolved value or None if not found
        """
        # Parse the reference - e.g., "profiles[0].token" or "services.Namespace"
        # Split by dots and brackets
        parts = re.split(r"\.|\[|\]", reference)
        parts = [p for p in parts if p]  # Remove empty strings

        if not parts:
            return None

        # Start with the stored variable name
        var_name = parts[0]
        if var_name not in self.context.stored_data:
            return None

        current = self.context.stored_data[var_name]

        # Navigate through the rest of the path
        for part in parts[1:]:
            try:
                # Check if it's an integer index
                if part.isdigit():
                    index = int(part)
                    if isinstance(current, (list, tuple)):
                        current = current[index]
                    else:
                        # Try to convert to list if it's iterable
                        try:
                            current = list(current)[index]
                        except (TypeError, IndexError):
                            return None
                else:
                    # It's an attribute name
                    if hasattr(current, part):
                        current = getattr(current, part)
                    elif isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        return None
            except (IndexError, AttributeError, KeyError, TypeError):
                return None

        return current

    def complete_show(self, text, line, _begidx, _endidx) -> list:
        """Autocomplete stored variable names for show command."""
        # Get the part being completed
        parts = line.split()
        if len(parts) <= 1 or (len(parts) == 2 and not line.endswith(" ")):
            # Completing the variable name
            return [name for name in self.context.stored_data if name.startswith(text)]
        return []

    def do_rm(self, line) -> None:
        """Remove stored data: rm <name>"""
        if not line:
            print("Usage: rm <name>")
            return
        if line in self.context.stored_data:
            del self.context.stored_data[line]
            if line in self.context.stored_metadata:
                del self.context.stored_metadata[line]
            print(f"{colorize('Removed:', 'yellow')} {colorize('$'+line, 'cyan')}")
        else:
            print(f"{colorize('Error:', 'red')} No stored data named '{line}'")

    def complete_rm(self, text, _line, _begidx, _endidx) -> list:
        """Autocomplete stored variable names for rm command."""
        return [name for name in self.context.stored_data if name.startswith(text)]

    def do_cls(self, _line) -> None:
        """Clear stored data."""
        self.context.stored_data.clear()
        self.context.stored_metadata.clear()
        print(f"{colorize('Cleared all stored data', 'yellow')}")
