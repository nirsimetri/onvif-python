"""Tests for CLI helper messages."""

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from onvif.cli.helpers.messages import print_interactive_intro


def make_args(**overrides):
    """Create CLI arguments with default values and optional overrides."""
    args = {
        "host": "192.168.1.17",
        "port": 8000,
        "digest": False,
        "https": False,
        "no_verify_ssl": False,
        "timeout": 10,
        "debug": False,
        "no_patch": False,
        "wsdl": None,
        "health_check_interval": 10,
    }
    args.update(overrides)
    return SimpleNamespace(**args)


def test_print_interactive_intro_basic():
    """Test the interactive introduction with default arguments."""
    args = make_args()

    with patch(
        "onvif.cli.helpers.messages.colorize",
        side_effect=lambda text, color: text,
    ) as mock_colorize:
        result = print_interactive_intro(args, "Device: Test Camera")

    assert isinstance(result, str)
    assert result

    # Core dynamic information
    assert args.host in result
    assert str(args.port) in result
    assert "Test Camera" in result

    # Always-present values must go through colorize
    colorized_values = [call.args[0] for call in mock_colorize.call_args_list]

    assert f"{args.host}:{args.port}" in colorized_values
    assert "WS-UsernameToken" in colorized_values


@pytest.mark.parametrize(
    ("attribute", "value", "expected_value"),
    [
        ("https", True, "True"),
        ("no_verify_ssl", True, "False"),
        ("timeout", 30, "30s"),
        ("debug", True, "True"),
        ("no_patch", True, "Disabled"),
        ("wsdl", "C:\\custom\\wsdl", "C:\\custom\\wsdl"),
        ("health_check_interval", 30, "30s"),
    ],
)
def test_print_interactive_intro_optional_branches(
    attribute,
    value,
    expected_value,
):
    """Test that optional CLI settings are displayed and colorized correctly."""
    args = make_args(**{attribute: value})

    with patch(
        "onvif.cli.helpers.messages.colorize",
        side_effect=lambda text, color: text,
    ) as mock_colorize:
        result = print_interactive_intro(args, "")

    assert isinstance(result, str)

    colorized_values = [call.args[0] for call in mock_colorize.call_args_list]

    assert expected_value in colorized_values


@pytest.mark.parametrize(
    ("digest", "expected"),
    [
        (True, "HTTP Digest"),
        (False, "WS-UsernameToken"),
    ],
)
def test_print_interactive_intro_auth_method(digest, expected):
    """Test that the configured authentication method is displayed correctly."""
    args = make_args(digest=digest)

    with patch(
        "onvif.cli.helpers.messages.colorize",
        side_effect=lambda text, color: text,
    ) as mock_colorize:
        print_interactive_intro(args, "")

    colorized_values = [call.args[0] for call in mock_colorize.call_args_list]

    assert expected in colorized_values
