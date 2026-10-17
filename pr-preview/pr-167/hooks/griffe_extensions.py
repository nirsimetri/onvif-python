"""Griffe extentions."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import griffe

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


class DocstringShortcodes(griffe.Extension):
    """Process supported Markdown shortcodes in Python docstrings."""

    def on_object(self, *, obj: griffe.Object, **kwargs) -> None:
        """Replace shortcodes in an object's docstring."""
        docstring = obj.docstring

        if docstring is None:
            return

        docstring.value = replace_docstring_shortcodes(docstring.value)
