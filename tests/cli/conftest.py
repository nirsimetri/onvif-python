"""Shared CLI test fixtures and helpers."""

import re

ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text):
    """Remove ANSI escape sequences from terminal output."""
    return ANSI_ESCAPE.sub("", text)
