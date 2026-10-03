"""Tests for the ONVIF CLI entry point."""

import runpy
from unittest.mock import patch


def test_cli_main_calls_main():
    """Test that the CLI entry point calls main()."""
    with patch("onvif.cli.main.main") as mock_main:
        runpy.run_module("onvif.cli.__main__", run_name="__main__")

    mock_main.assert_called_once_with()
