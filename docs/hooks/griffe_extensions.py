"""Griffe extensions."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from typing import Any

import griffe
from griffe import Extension, Function, Object

_SHORTCODES_PATH = Path(__file__).with_name("shortcodes.py")
_SPEC = importlib.util.spec_from_file_location(
    "onvif_doc_shortcodes",
    _SHORTCODES_PATH,
)

if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Cannot load shortcode module: {_SHORTCODES_PATH}")

_SHORTCODES = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_SHORTCODES)

replace_docstring_shortcodes = _SHORTCODES.replace_docstring_shortcodes

# Join words split across lines after a hyphen.
_HYPHENATED_LINE_BREAK = re.compile(r"(?<=[A-Za-z])-\s*\n\s*(?=[A-Za-z])")


def normalize_docstring_line_breaks(text: str) -> str:
    """Normalize words split across lines in docstrings."""
    return _HYPHENATED_LINE_BREAK.sub("-", text)


class DocstringShortcodes(griffe.Extension):
    """Process supported Markdown shortcodes in Python docstrings."""

    def on_object(self, *, obj: griffe.Object, **kwargs) -> None:
        """Replace shortcodes in an object's docstring."""
        docstring = obj.docstring

        if docstring is None:
            return

        docstring.value = normalize_docstring_line_breaks(docstring.value)
        docstring.value = replace_docstring_shortcodes(docstring.value)

        docstring.value = replace_docstring_shortcodes(docstring.value)


# Match ONVIF-style method names, such as GetServices and GetServiceCapabilities.
_METHOD_REFERENCE = re.compile(
    r"(?<![\w.`\[])"
    r"(?P<name>(?:Get|Set|Create|Delete|Add|Remove|Start|Stop|"
    r"Renew|Unsubscribe|Subscribe|Pause|Resume|Send|Find|Load|"
    r"Save|Activate|Reboot|Restore|Upgrade|SystemReboot)"
    r"[A-Z][A-Za-z0-9_]*)"
    r"(?![\w`.\]])"
)


class DocstringCrossReferences(Extension):
    """Automatically link API method references in docstrings."""

    def on_object(self, *, obj: Object, **kwargs: Any) -> None:
        """Link references to methods in the same parent class."""
        if not isinstance(obj, Function):
            return

        docstring = obj.docstring
        if docstring is None or obj.parent is None:
            return

        docstring.value = self._link_methods(docstring.value, obj)

    @staticmethod
    def _link_methods(text: str, obj: Function) -> str:
        """Resolve method references against the parent class."""
        parent = obj.parent
        if parent is None:
            return text

        members = getattr(parent, "members", {})
        method_names = {
            name for name, member in members.items() if isinstance(member, Function)
        }

        if not method_names:
            return text

        def replace(match: re.Match[str]) -> str:
            name = match.group("name")

            if name not in method_names:
                return name

            target = members[name]
            return f"[`{name}`][{target.path}]"

        return _METHOD_REFERENCE.sub(replace, text)
