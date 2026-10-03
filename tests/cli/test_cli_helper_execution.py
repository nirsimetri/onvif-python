"""Tests for CLI helper execution."""

import warnings
from unittest.mock import Mock, patch

import pytest

from onvif.cli.helpers.execution import (
    execute_command,
    setup_warning_format,
)


class FakeService:  # pylint: disable=too-few-public-methods
    """Minimal fake service used to test CLI command execution."""

    def __init__(self, result=None):
        self.result = result

    def GetProfiles(self, **kwargs):  # pylint: disable=invalid-name
        """Return a predictable result for GetProfiles."""
        return self.result or {
            "method": "GetProfiles",
            "params": kwargs,
        }


class FakeClient:  # pylint: disable=too-few-public-methods
    """Minimal fake client used to provide services to CLI command execution."""

    def __init__(self, service=None):
        self.service = service or FakeService()

    def media(self):
        """Return the fake media service."""
        return self.service


@pytest.fixture
def fake_service():
    """Return a reusable fake media service."""
    return FakeService()


@pytest.fixture
def fake_client(fake_service):
    """Return a client using the reusable fake media service."""
    return FakeClient(fake_service)


def test_execute_command_without_params(fake_client):
    """Test command execution without parameters."""
    result = execute_command(
        fake_client,
        "media",
        "GetProfiles",
    )

    assert result == {
        "method": "GetProfiles",
        "params": {},
    }


def test_execute_command_with_params(fake_client):
    """Test command execution with JSON parameters."""
    result = execute_command(
        fake_client,
        "media",
        "GetProfiles",
        '{"ProfileToken": "profile_1"}',
    )

    assert result == {
        "method": "GetProfiles",
        "params": {
            "ProfileToken": "profile_1",
        },
    }


def test_execute_command_with_simple_params(fake_client):
    """Test command execution with simple key-value parameters."""
    result = execute_command(
        fake_client,
        "media",
        "GetProfiles",
        "ProfileToken=profile_1",
    )

    assert result == {
        "method": "GetProfiles",
        "params": {
            "ProfileToken": "profile_1",
        },
    }


def test_execute_command_normalizes_service_name():
    """Test that service names are normalized before lookup."""
    service = Mock()
    service.GetProfiles.return_value = "result"

    client = Mock()
    client.media.return_value = service

    result = execute_command(
        client,
        "MEDIA",
        "GetProfiles",
    )

    assert result == "result"
    client.media.assert_called_once_with()
    service.GetProfiles.assert_called_once_with()


def test_execute_command_calls_method_with_parsed_params(fake_service):
    """Test that parsed parameters are passed to the service method."""
    fake_service.GetProfiles = Mock(return_value="result")
    client = FakeClient(fake_service)

    params = '{"ProfileToken": "profile_1", "Include": true}'

    result = execute_command(
        client,
        "media",
        "GetProfiles",
        params,
    )

    assert result == "result"
    fake_service.GetProfiles.assert_called_once_with(
        ProfileToken="profile_1",
        Include=True,
    )


def test_execute_command_empty_params_string(fake_service):
    """Test command execution with an empty parameter string."""
    fake_service.GetProfiles = Mock(return_value="result")
    client = FakeClient(fake_service)

    result = execute_command(
        client,
        "media",
        "GetProfiles",
        "",
    )

    assert result == "result"
    fake_service.GetProfiles.assert_called_once_with()


def test_execute_command_none_params(fake_service):
    """Test command execution when parameters are omitted."""
    fake_service.GetProfiles = Mock(return_value="result")
    client = FakeClient(fake_service)

    result = execute_command(
        client,
        "media",
        "GetProfiles",
        None,
    )

    assert result == "result"
    fake_service.GetProfiles.assert_called_once_with()


def test_execute_command_unknown_service():
    """Test that an unknown service raises ValueError."""
    client = Mock()
    client.media.side_effect = AttributeError("service not found")

    with pytest.raises(ValueError) as exc_info:
        execute_command(
            client,
            "media",
            "GetProfiles",
        )

    message = str(exc_info.value)

    assert "Unknown service:" in message
    assert "media" in message


def test_execute_command_unknown_method():
    """Test that an unknown method raises ValueError."""
    client = Mock()
    client.media.return_value = object()

    with pytest.raises(ValueError) as exc_info:
        execute_command(
            client,
            "media",
            "GetProfiles",
        )

    message = str(exc_info.value)

    assert "Unknown method" in message
    assert "GetProfiles" in message
    assert "media" in message


def test_execute_command_preserves_method_attribute_error_as_value_error():
    """Test that a method lookup AttributeError raises ValueError."""

    class Service:  # pylint: disable=too-few-public-methods
        """Service with property."""

        @property
        def GetProfiles(self):  # pylint: disable=invalid-name
            """Unavailable method."""
            raise AttributeError("method unavailable")

    client = Mock()
    client.media.return_value = Service()

    with pytest.raises(ValueError) as exc_info:
        execute_command(
            client,
            "media",
            "GetProfiles",
        )

    assert "Unknown method" in str(exc_info.value)


def test_execute_command_propagates_method_exception(fake_service):
    """Test that exceptions raised by the service method are propagated."""
    expected_error = RuntimeError("camera failure")
    fake_service.GetProfiles = Mock(side_effect=expected_error)
    client = FakeClient(fake_service)

    with pytest.raises(RuntimeError, match="camera failure"):
        execute_command(
            client,
            "media",
            "GetProfiles",
        )

    fake_service.GetProfiles.assert_called_once_with()


def test_execute_command_uses_parse_json_params():
    """Test that provided parameters are parsed with parse_json_params."""
    client = Mock()
    service = Mock()
    method = Mock(return_value="result")

    client.media.return_value = service
    service.GetProfiles = method

    with patch(
        "onvif.cli.helpers.execution.parse_json_params",
        return_value={"ProfileToken": "profile_1"},
    ) as mock_parse:
        result = execute_command(
            client,
            "media",
            "GetProfiles",
            "some params",
        )

    assert result == "result"
    mock_parse.assert_called_once_with("some params")
    method.assert_called_once_with(ProfileToken="profile_1")


def test_execute_command_does_not_parse_missing_params():
    """Test that missing parameters do not invoke parse_json_params."""
    client = Mock()
    service = Mock()
    method = Mock(return_value="result")

    client.media.return_value = service
    service.GetProfiles = method

    with patch(
        "onvif.cli.helpers.execution.parse_json_params",
    ) as mock_parse:
        result = execute_command(
            client,
            "media",
            "GetProfiles",
            None,
        )

    assert result == "result"
    mock_parse.assert_not_called()
    method.assert_called_once_with()


def test_execute_command_invalid_params_propagate():
    """Test that parameter parsing errors are propagated."""
    client = Mock()
    service = Mock()
    client.media.return_value = service
    service.GetProfiles = Mock()

    with patch(
        "onvif.cli.helpers.execution.parse_json_params",
        side_effect=ValueError("invalid JSON"),
    ):
        with pytest.raises(ValueError, match="invalid JSON"):
            execute_command(
                client,
                "media",
                "GetProfiles",
                "{invalid}",
            )


def test_setup_warning_format():
    """Test that the custom warning format is configured correctly."""
    original_formatter = warnings.formatwarning

    try:
        setup_warning_format()

        assert warnings.formatwarning.__name__ == "custom_warning_format"

        result = warnings.formatwarning(
            "Something went wrong",
            UserWarning,
            "test.py",
            123,
        )

        assert result == "UserWarning: Something went wrong\n"
    finally:
        warnings.formatwarning = original_formatter
