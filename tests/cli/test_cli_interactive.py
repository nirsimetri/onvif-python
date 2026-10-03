# pylint: disable=protected-access
"""Tests for the interactive ONVIF CLI shell."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from onvif.cli.interactive import InteractiveShell


def make_shell():
    """Create a minimally initialized interactive shell for unit tests."""
    shell = object.__new__(InteractiveShell)

    shell.client = Mock()
    shell.args = SimpleNamespace(
        username="admin",
        host="camera",
        port=80,
        debug=False,
    )
    shell.current_service = None
    shell.current_service_name = None
    shell.stored_data = {}
    shell.stored_metadata = {}
    shell._last_result = None
    shell._last_method = None
    shell._last_service_name = None
    shell._last_operation_timestamp = None
    shell.base_commands = [
        "capabilities",
        "caps",
        "services",
        "help",
        "exit",
        "store",
        "rm",
        "show",
        "cls",
        "clear",
        "info",
        "debug",
        "ls",
        "cd",
        "shortcuts",
        "desc",
        "type",
    ]
    shell.prompt = ""
    shell.device_info_text = ""
    shell.intro = ""
    shell._stop_health_check = Mock()
    return shell


class TestSplitMultiCommands:
    """Test splitting chained interactive commands."""

    def test_splits_top_level_commands(self):
        """Test that top-level commands are split on double ampersands."""
        shell = make_shell()

        result = shell._split_multi_commands("media && GetProfiles && ls")

        assert result == ["media", "GetProfiles", "ls"]

    def test_preserves_quoted_and_nested_commands(self):
        """Test that separators inside quotes and brackets are preserved."""
        shell = make_shell()

        result = shell._split_multi_commands(
            'command {"value": "a && b"} && other [1, "x && y"]'
        )

        assert result == [
            'command {"value": "a && b"}',
            'other [1, "x && y"]',
        ]


class TestResolveStoredReference:
    """Test resolving values from stored command results."""

    @pytest.mark.parametrize(
        ("reference", "expected"),
        [
            ("value", 42),
            ("profile.name", "camera"),
            ("profiles[0]", "first"),
            ("profiles[1].token", "second-token"),
        ],
    )
    def test_resolves_supported_references(self, reference, expected):
        """Test resolving dictionary, attribute, and list references."""
        shell = make_shell()
        shell.stored_data = {
            "value": 42,
            "profile": {"name": "camera"},
            "profiles": [
                "first",
                {"token": "second-token"},
            ],
        }

        assert shell._resolve_stored_reference(reference) == expected

    def test_returns_none_for_unknown_reference(self):
        """Test that an unknown stored reference returns None."""
        shell = make_shell()

        assert shell._resolve_stored_reference("missing.value") is None


class TestSubstituteStoredReferences:
    """Test substituting stored values into command parameters."""

    def test_substitutes_stored_values(self):
        """Test that stored references are replaced with JSON values."""
        shell = make_shell()
        shell.stored_data = {"token": "abc123", "count": 5}

        result = shell._substitute_stored_references(
            '{"Token": $token, "Count": $count}'
        )

        assert result == '{"Token": "abc123", "Count": 5}'

    def test_keeps_unresolved_references(self, capsys):
        """Test that unresolved references remain unchanged and emit a warning."""
        shell = make_shell()

        result = shell._substitute_stored_references('{"Token": $missing}')

        assert result == '{"Token": $missing}'

        assert "Cannot resolve $missing" in capsys.readouterr().out


class TestUpdatePrompt:
    """Test interactive shell prompt generation."""

    def test_builds_root_prompt(self):
        """Test that the root prompt contains connection information."""
        shell = make_shell()

        shell.update_prompt()

        assert shell.prompt == "admin@camera:80 > "

    def test_builds_service_prompt(self):
        """Test that the service prompt includes the current service name."""
        shell = make_shell()
        shell.current_service_name = "media"

        shell.update_prompt()

        assert shell.prompt == "admin@camera:80/media > "


class TestGetSuggestions:
    """Test command and service suggestions."""

    def test_suggests_root_commands(self, monkeypatch):
        """Test that matching root commands are returned."""
        shell = make_shell()

        monkeypatch.setattr(
            "onvif.cli.interactive.get_device_available_services",
            lambda _client: ["media", "events"],
        )

        result = shell.get_suggestions("me")

        assert "media" in result

    def test_limits_suggestions(self, monkeypatch):
        """Test that suggestions are limited to five results."""
        shell = make_shell()

        monkeypatch.setattr(
            "onvif.cli.interactive.get_device_available_services",
            lambda _client: [f"service{i}" for i in range(10)],
        )

        result = shell.get_suggestions("service")

        assert len(result) == 5


class TestCompleteNames:
    """Test command name completion."""

    def test_completes_root_commands_and_services(self, monkeypatch):
        """Test completion of root-level commands and services."""
        shell = make_shell()

        monkeypatch.setattr(
            "onvif.cli.interactive.get_device_available_services",
            lambda _client: ["media", "events"],
        )

        result = shell.completenames("me")

        assert "media" in result

    def test_completes_service_methods(self, monkeypatch):
        """Test completion of methods while inside a service."""
        shell = make_shell()
        shell.current_service = Mock()

        monkeypatch.setattr(
            "onvif.cli.interactive.get_service_methods",
            lambda _service: ["GetProfiles", "GetStreamUri"],
        )

        result = shell.completenames("getp")

        assert result == ["GetProfiles"]


class TestEnterService:
    """Test entering an ONVIF service."""

    def test_enters_service_without_required_arguments(self, monkeypatch):
        """Test entering a service that does not require arguments."""
        shell = make_shell()
        service = Mock()

        monkeypatch.setattr(
            "onvif.cli.interactive.get_device_available_services",
            lambda _client: ["media"],
        )
        monkeypatch.setattr(
            "onvif.cli.interactive.get_service_required_args",
            lambda _service: [],
        )
        monkeypatch.setattr(
            "onvif.cli.interactive.get_service_methods",
            lambda _service: ["GetProfiles"],
        )
        shell.client.media.return_value = service

        shell.do_enter_service("media")

        assert shell.current_service is service
        assert shell.current_service_name == "media"
        assert shell.prompt.endswith("/media > ")

    def test_rejects_unknown_service(self, monkeypatch, capsys):
        """Test that an unavailable service is rejected."""
        shell = make_shell()

        monkeypatch.setattr(
            "onvif.cli.interactive.get_device_available_services",
            lambda _client: ["media"],
        )

        shell.do_enter_service("events")

        assert "Unknown service" in capsys.readouterr().out
        assert shell.current_service is None


class TestExecuteServiceMethod:
    """Test executing methods on the active ONVIF service."""

    def test_rejects_execution_without_service(self, capsys):
        """Test that method execution fails outside service mode."""
        shell = make_shell()

        shell.execute_service_method("GetProfiles", "")

        assert "Not in service mode" in capsys.readouterr().out

    def test_executes_method_and_stores_last_result(self, capsys):
        """Test executing a service method and recording its result."""
        shell = make_shell()
        shell.current_service = Mock()
        shell.current_service_name = "media"
        shell.current_service.GetProfiles.return_value = {"Profiles": []}

        shell.execute_service_method("GetProfiles", "")

        assert shell._last_result == {"Profiles": []}
        assert shell._last_method == "GetProfiles"
        assert shell._last_service_name == "media"
        assert "{'Profiles': []}" in capsys.readouterr().out

    def test_passes_json_parameters_to_method(self):
        """Test that parsed command parameters are passed to the service method."""
        shell = make_shell()
        shell.current_service = Mock()
        shell.current_service.GetProfile.return_value = "profile"

        shell.execute_service_method(
            "GetProfile",
            '{"ProfileToken": "token-1"}',
        )

        shell.current_service.GetProfile.assert_called_once_with(ProfileToken="token-1")


class TestStoreData:
    """Test storing command results for later reuse."""

    def test_stores_last_result(self):
        """Test storing the most recent command result."""
        shell = make_shell()
        shell._last_result = {"value": 123}
        shell.current_service_name = "media"
        shell._last_method = "GetProfiles"

        shell.do_store("profiles")

        assert shell.stored_data["profiles"] == {"value": 123}
        assert shell.stored_metadata["profiles"] == {
            "service": "media",
            "method": "GetProfiles",
        }

    def test_rejects_invalid_name(self, capsys):
        """Test that invalid stored variable names are rejected."""
        shell = make_shell()
        shell._last_result = {"value": 123}

        shell.do_store("123profiles")

        assert "Invalid name" in capsys.readouterr().out
        assert not shell.stored_data


# pylint: disable=too-few-public-methods
class TestRemoveData:
    """Test removing stored command results."""

    def test_removes_stored_data_and_metadata(self):
        """Test that stored data and its metadata are removed together."""
        shell = make_shell()
        shell.stored_data["profiles"] = {"value": 1}
        shell.stored_metadata["profiles"] = {"service": "media"}

        shell.do_rm("profiles")

        assert "profiles" not in shell.stored_data
        assert "profiles" not in shell.stored_metadata


class TestServiceMode:
    """Test entering and leaving service mode."""

    def test_exits_service_mode(self):
        """Test that leaving service mode resets service state."""
        shell = make_shell()
        shell.current_service = Mock()
        shell.current_service_name = "media"

        shell.do_up("")

        assert shell.current_service is None
        assert shell.current_service_name is None
        assert shell.prompt == "admin@camera:80 > "

    def test_reports_when_not_in_service_mode(self, capsys):
        """Test the message shown when leaving service mode from root mode."""
        shell = make_shell()

        shell.do_up("")

        assert "Not in service mode" in capsys.readouterr().out


# pylint: disable=too-few-public-methods
class TestClearStoredData:
    """Test clearing all stored command results."""

    def test_clears_data_and_metadata(self):
        """Test that all stored data and metadata are removed."""
        shell = make_shell()
        shell.stored_data["profiles"] = {}
        shell.stored_metadata["profiles"] = {}

        shell.do_cls("")

        assert not shell.stored_data
        assert not shell.stored_metadata


# pylint: disable=too-few-public-methods
class TestExit:
    """Test interactive shell shutdown."""

    def test_stops_health_check_and_returns_true(self, capsys):
        """Test that exiting signals the health-check thread and stops the shell."""
        shell = make_shell()

        assert shell.do_exit("") is True
        shell._stop_health_check.set.assert_called_once()
        assert "Goodbye!" in capsys.readouterr().out
