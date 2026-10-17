"""Shortcodes hook.

Origin source:
https://github.com/squidfunk/mkdocs-material/blob/master/src/overrides/hooks/shortcodes.py
"""

# Copyright (c) 2016-2025 Martin Donath <martin.donath@squidfunk.com>

# Modified by Nirsimetri Technologies® for ONVIF Python documentation.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

# pylint: disable=unused-argument,redefined-builtin
# pylint: disable=unnecessary-lambda,too-many-branches
# pylint: disable=too-many-return-statements
from __future__ import annotations

import posixpath
import re
from re import Match

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

REPOSITORY = "https://github.com/nirsimetri/onvif-python"
RELEASE_ENDPOINT = "onvif-python/releases"
EXAMPLE_PATH = "blob/main/examples"
MODULE_PATH = "blob/main/onvif"

ICON_FOR_VERSION = "material-source-pull"
ICON_FOR_ONVIF_VERSION = "material-app-badging"
ICON_FOR_INTERNAL = "material-lock-outline"
ICON_FOR_EXCEPTION = "material-alert-circle-outline"
ICON_FOR_ERROR_HANDLER = "material-reload-alert"
ICON_FOR_SERVICE_ENTRY_POINT = "material-my-location"
ICON_FOR_FEATURE = "material-toggle-switch"
ICON_FOR_PLUGIN = "material-puzzle-outline"
ICON_FOR_UTILITY = "material-hammer-wrench"
ICON_FOR_EXAMPLE_VIEW = "material-file-eye"
ICON_FOR_EXAMPLE_FILE = "material-file-code"
ICON_FOR_MODULE = "material-code-block-tags"
ICON_FOR_DEMO = "material-github"
ICON_FOR_DEFAULT_VALUE = "material-water"
ICON_FOR_DEFAULT_NONE = "material-water-outline"
ICON_FOR_DEFAULT_COMPUTED = "material-water-check"
ICON_FOR_METADATA = "material-list-box-outline"
ICON_FOR_REQUIRED = "material-alert"
ICON_FOR_EXPERIMENTAL = "material-flask-outline"

# -----------------------------------------------------------------------------
# For griffe
# -----------------------------------------------------------------------------


def replace_docstring_shortcodes(docstring: str) -> str:
    """Replace supported shortcodes in Python docstrings."""
    return re.sub(
        r"<!-- md:(\w+)(.*?)\s*-->",
        lambda match: replace(match),
        docstring,
        flags=re.I | re.M,
    )


# -----------------------------------------------------------------------------
# Hooks
# -----------------------------------------------------------------------------


def on_page_markdown(
    markdown: str,
    *,
    page: Page,
    config: MkDocsConfig,
    files: Files,
):
    """Replace supported shortcodes in page Markdown."""
    return re.sub(
        r"<!-- md:(\w+)(.*?)\s*-->",
        lambda match: replace(match, page, files),
        markdown,
        flags=re.I | re.M,
    )


# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------


def replace(match: Match, page: Page | None = None, files: Files | None = None):
    """Shortcodes replacer."""

    type, args = match.groups()
    args = args.strip()

    match type:
        case "version":
            return _badge_for_version(args, page, files)
        case "onvif_version":
            return _badge_for_onvif_version(args)
        case "flag":
            return flag(args, page, files)
        case "option":
            return option(args)
        case "setting":
            return setting(args)
        case "internal":
            return _badge_for_internal(args, page, files)
        case "exception":
            return _badge_for_exception(args, page, files)
        case "error_handler":
            return _badge_for_error_handler(args, page, files)
        case "entry_point":
            return _badge_for_entry_point(args, page, files)
        case "feature":
            return _badge_for_feature(args, page, files)
        case "plugin":
            return _badge_for_plugin(args, page, files)
        case "utility":
            return _badge_for_utility(args, page, files)
        case "example":
            return _badge_for_example(args, page, files)
        case "example_view":
            return _badge_for_example_view(args, page, files)
        case "example_file":
            return _badge_for_example_file(args, page, files)
        case "module":
            return _badge_for_module(args, page, files)
        case "demo":
            return _badge_for_demo(args, page, files)
        case "default":
            if args == "none":
                return _badge_for_default_none(page, files)
            if args == "computed":
                return _badge_for_default_computed(page, files)
            return _badge_for_default(args, page, files)
        case _:
            raise RuntimeError(f"Unknown shortcode: {type}")


def flag(args: str, page: Page, files: Files):
    """Create a flag of a specific type."""
    type, *_ = args.split(" ", 1)

    match type:
        case "experimental":
            return _badge_for_experimental(page, files)
        case "required":
            return _badge_for_required(page, files)
        case "metadata":
            return _badge_for_metadata(page, files)
        case _:
            raise RuntimeError(f"Unknown type: {type}")


def option(type: str):
    """Create a linkable option."""
    _, *_, name = re.split(r"[.:]", type)
    return f"[`{name}`](#+{type}){{ #+{type} }}\n\n"


def setting(type: str):
    """Create a linkable setting - @todo append them to the bottom of the page."""
    _, *_, name = re.split(r"[.*]", type)
    return f"`{name}` {{ #{type} }}\n\n[{type}]: #{type}\n\n"


# -----------------------------------------------------------------------------


def _resolve_path(path: str, page: Page, files: Files):
    """Resolve path of file relative to given page - the posixpath always includes
    one additional level of `..` which we need to remove."""
    path, anchor, *_ = f"{path}#".split("#")
    path = _resolve(files.get_file_from_path(path), page)
    return "#".join([path, anchor]) if anchor else path


def _resolve(file: File, page: Page):
    """Resolve path of file relative to given page - the posixpath always includes
    one additional level of `..` which we need to remove."""
    path = posixpath.relpath(file.src_uri, page.file.src_uri)
    return posixpath.sep.join(path.split(posixpath.sep)[1:])


# -----------------------------------------------------------------------------


# Create badge
def _badge(icon: str, text: str = "", type: str = "", title: str = ""):
    classes = f"mdx-badge mdx-badge--{type}" if type else "mdx-badge"

    return "".join(
        [
            f'<span class="{classes}">',
            *(
                [f'<span class="mdx-badge__icon" title="{title}">{icon}</span>']
                if icon
                else []
            ),
            *([f'<span class="mdx-badge__text">{text}</span>'] if text else []),
            "</span>",
        ]
    )


# Create badge for pacakge version
def _badge_for_version(text: str, page: Page | None = None, files: Files | None = None):
    path = f"releases.md#v{text}"

    if page is not None and files is not None:
        href = _resolve_path(path, page, files)
    else:
        href = f"/{RELEASE_ENDPOINT}/#v{text}"

    return _badge(
        icon=f":{ICON_FOR_VERSION}:",
        text=f"[`v{text}`]({href})" if text else "",
        title="Minimum package version",
    )


# Create badge for ONVIF version
def _badge_for_onvif_version(args: str):
    """Create a badge linking an ONVIF version to its specification."""
    match = re.fullmatch(r"(\S+)\s+(https?://\S+)", args.strip())

    if not match:
        raise ValueError("Invalid onvif_version shortcode. Expected: VERSION URL")

    version, href = match.groups()

    return _badge(
        icon=f":{ICON_FOR_ONVIF_VERSION}:",
        text=f"[`{version}`]({href}){{.no-external-icon }}",
        title="Minimum ONVIF version",
    )


# Create badge for internal
def _badge_for_internal(text: str, page: Page, files: Files):
    return _badge(
        icon=f":{ICON_FOR_INTERNAL}:",
        title=text or "Internal implementation",
        text=f"*{text}*" if text else "",
    )


# Create badge for exception
def _badge_for_exception(text: str, page: Page, files: Files):
    return _badge(
        icon=f":{ICON_FOR_EXCEPTION}:",
        title=text or "Exception type",
        text=f"*{text}*" if text else "",
    )


# Create badge for error handler
def _badge_for_error_handler(text: str, page: Page, files: Files):
    return _badge(
        icon=f":{ICON_FOR_ERROR_HANDLER}:",
        title=text or "Error handler",
        text=f"*{text}*" if text else "",
    )


# Create badge for entry point
def _badge_for_entry_point(text: str, page: Page, files: Files):
    return _badge(
        icon=f":{ICON_FOR_SERVICE_ENTRY_POINT}:",
        title=text or "ONVIF Service entry point",
        text=f"*{text}*" if text else "",
    )


# Create badge for feature
def _badge_for_feature(text: str, page: Page, files: Files):
    return _badge(
        icon=f":{ICON_FOR_FEATURE}:",
        title=text or "Optional feature",
        text=f"*{text}*" if text else "",
    )


# Create badge for plugin
def _badge_for_plugin(text: str, page: Page, files: Files):
    return _badge(
        icon=f":{ICON_FOR_PLUGIN}:",
        title=text or "Plugin",
        text=f"*{text}*" if text else "",
    )


# Create badge for utility
def _badge_for_utility(text: str, page: Page, files: Files):
    return _badge(
        icon=f":{ICON_FOR_UTILITY}:",
        title=text or "Utility",
        text=f"*{text}*" if text else "",
    )


# Create badge for example
def _badge_for_example(text: str, page: Page, files: Files):
    return "\n".join(
        [
            _badge_for_example_file(text, page, files),
            _badge_for_example_view(text, page, files),
        ]
    )


# Create badge for example view
def _badge_for_example_view(text: str, page: Page, files: Files):
    href = f"{REPOSITORY}/{EXAMPLE_PATH}/{text}"
    return _badge(
        icon=f"[:{ICON_FOR_EXAMPLE_VIEW}:]({href}){{.no-external-icon }}",
        title=f"View example `{text}`",
        type="right",
    )


# Create badge for example download
def _badge_for_example_file(text: str, page: Page, files: Files):
    href = f"{REPOSITORY}/{EXAMPLE_PATH}/{text}"
    return _badge(
        icon=f"[:{ICON_FOR_EXAMPLE_FILE}:]({href}){{.no-external-icon }}",
        title="Inspect example file",
        text=f"[`{text}`]({href})",
        type="right",
    )


# Create badge for module
def _badge_for_module(text: str, page: Page, files: Files):
    href = f"{REPOSITORY}/{MODULE_PATH}/{text}"
    return _badge(
        icon=f"[:{ICON_FOR_MODULE}:]({href}){{.no-external-icon }}",
        title=f"Inspect module `{text}`",
        type="right",
    )


# Create badge for demo repository
def _badge_for_demo(text: str, page: Page, files: Files):
    href = text
    return _badge(
        icon=f"[:{ICON_FOR_DEMO}:]({href})",
        title="Go to repository",
        text=f"*{text}*" if text else "",
        type="right",
    )


# Create badge for default value
def _badge_for_default(text: str, page: Page, files: Files):
    return _badge(
        icon=f":{ICON_FOR_DEFAULT_VALUE}:", title=text or "Default value", text=text
    )


# Create badge for empty default value
def _badge_for_default_none(page: Page, files: Files):
    return _badge(icon=f":{ICON_FOR_DEFAULT_NONE}:", title="Default value is empty")


# Create badge for computed default value
def _badge_for_default_computed(page: Page, files: Files):
    return _badge(
        icon=f":{ICON_FOR_DEFAULT_COMPUTED}:", title="Default value is computed"
    )


# Create badge for metadata property flag
def _badge_for_metadata(page: Page, files: Files):
    return _badge(icon=f":{ICON_FOR_METADATA}:", title="Metadata property")


# Create badge for required value flag
def _badge_for_required(page: Page, files: Files):
    return _badge(icon=f":{ICON_FOR_REQUIRED}:", title="Required value")


# Create badge for experimental flag
def _badge_for_experimental(page: Page, files: Files):
    return _badge(icon=f":{ICON_FOR_EXPERIMENTAL}:", title="Experimental")
