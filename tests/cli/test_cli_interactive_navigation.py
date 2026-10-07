# pylint: disable=protected-access
"""Tests for ONVIF interactive shell navigation commands."""

from unittest.mock import MagicMock, patch

from onvif.cli.interactive.navigation import NavigationCommands

from .conftest import strip_ansi


def create_args(**overrides):
    """Create mocked CLI arguments."""
    args = MagicMock()
    args.debug = overrides.get("debug", False)
    return args


def create_context(**overrides):
    """Create a mocked shell context."""
    context = MagicMock()

    context.args = create_args(**overrides)
    context.client = overrides.get("client", MagicMock())

    context.current_service = overrides.get("current_service", None)
    context.current_service_name = overrides.get("current_service_name", None)

    context.base_commands = overrides.get(
        "base_commands",
        [
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
        ],
    )

    return context


def create_commands(**overrides):
    """Create NavigationCommands with mocked shell dependencies."""
    commands = NavigationCommands()
    commands.context = create_context(**overrides)
    commands._display_grid = MagicMock()
    commands.update_prompt = MagicMock()
    commands._resolve_stored_reference = MagicMock()
    return commands


class TestNavigationCommandsList:
    """Test the ls command."""

    def test_do_ls_in_root_mode(self):
        """Verify ls displays services and base commands in root mode."""
        commands = create_commands()

        services = ["devicemgmt", "media"]

        with patch(
            "onvif.cli.interactive.navigation.get_device_available_services",
            return_value=services,
        ):
            commands.do_ls("")

        commands._display_grid.assert_called_once_with(
            services + commands.context.base_commands
        )

    def test_do_ls_in_service_mode(self):
        """Verify ls displays service methods and helper commands."""
        service = MagicMock()
        commands = create_commands(current_service=service)

        methods = ["GetDeviceInformation", "GetCapabilities"]

        with patch(
            "onvif.cli.interactive.navigation.get_service_methods",
            return_value=methods.copy(),
        ):
            commands.do_ls("")

        commands._display_grid.assert_called_once()

        displayed = commands._display_grid.call_args.args[0]

        assert displayed[:2] == methods
        assert len(displayed) == 4
        assert "type" in displayed[2]
        assert "desc" in displayed[3]

    def test_do_ls_displays_helper_commands_when_service_has_no_methods(self):
        """Verify ls displays helper commands when a service has no methods."""
        commands = create_commands(current_service=MagicMock())

        with patch(
            "onvif.cli.interactive.navigation.get_service_methods",
            return_value=[],
        ):
            commands.do_ls("")

        commands._display_grid.assert_called_once()

        displayed = commands._display_grid.call_args.args[0]

        assert len(displayed) == 2
        assert "type" in displayed[0]
        assert "desc" in displayed[1]

    def test_do_ls_prints_no_commands_when_root_is_empty(self, capsys):
        """Verify ls reports when no root commands or services are available."""
        commands = create_commands(base_commands=[])

        with patch(
            "onvif.cli.interactive.navigation.get_device_available_services",
            return_value=[],
        ):
            commands.do_ls("")

        commands._display_grid.assert_not_called()
        assert "No commands available" in capsys.readouterr().out


class TestNavigationCommandsCd:
    """Test the cd command."""

    def test_do_cd_without_service_name(self, capsys):
        """Verify cd displays usage and available services without an argument."""
        commands = create_commands()

        with patch(
            "onvif.cli.interactive.navigation.get_device_available_services",
            return_value=["devicemgmt", "media"],
        ):
            result = commands.do_cd("")

        assert result is None

        output = capsys.readouterr().out
        assert "Usage: cd <service_name>" in output
        assert "Available services:" in output
        assert "devicemgmt" in output
        assert "media" in output

    def test_do_cd_delegates_to_enter_service(self):
        """Verify cd delegates service entry to do_enter_service."""
        commands = create_commands()

        with patch.object(commands, "do_enter_service") as enter_service:
            commands.do_cd("devicemgmt")

        enter_service.assert_called_once_with("devicemgmt")

    def test_complete_cd_returns_matching_services(self):
        """Verify cd completion returns matching service names."""
        commands = create_commands()

        with patch(
            "onvif.cli.interactive.navigation.get_device_available_services",
            return_value=["devicemgmt", "media", "events"],
        ):
            result = commands.complete_cd("dev", "", 0, 3)

        assert result == ["devicemgmt"]

    def test_complete_cd_is_case_insensitive(self):
        """Verify cd completion is case-insensitive."""
        commands = create_commands()

        with patch(
            "onvif.cli.interactive.navigation.get_device_available_services",
            return_value=["DeviceMgmt", "Media"],
        ):
            result = commands.complete_cd("device", "", 0, 6)

        assert result == ["DeviceMgmt"]

    def test_complete_cd_returns_empty_for_no_match(self):
        """Verify cd completion returns no results when nothing matches."""
        commands = create_commands()

        with patch(
            "onvif.cli.interactive.navigation.get_device_available_services",
            return_value=["devicemgmt", "media"],
        ):
            result = commands.complete_cd("xyz", "", 0, 3)

        assert result == []


class TestNavigationCommandsUp:
    """Test the up command."""

    def test_do_up_exits_service_mode(self, capsys):
        """Verify up clears the current service and updates the prompt."""
        service = MagicMock()
        commands = create_commands(
            current_service=service,
            current_service_name="devicemgmt",
        )

        commands.do_up("")

        assert commands.context.current_service is None
        assert commands.context.current_service_name is None
        commands.update_prompt.assert_called_once_with()

        output = capsys.readouterr().out
        assert "Exited service:" in output
        assert "devicemgmt" in output

    def test_do_up_when_not_in_service_mode(self, capsys):
        """Verify up reports when already in root mode."""
        commands = create_commands()

        commands.do_up("")

        commands.update_prompt.assert_not_called()
        assert "Not in service mode" in capsys.readouterr().out


class TestNavigationCommandsEnterService:
    """Test entering ONVIF service mode."""

    def test_do_enter_service_unknown_service(self, capsys):
        """Verify unknown services are rejected."""
        commands = create_commands()

        with patch(
            "onvif.cli.interactive.navigation.get_device_available_services",
            return_value=["devicemgmt", "media"],
        ):
            commands.do_enter_service("unknown")

        output = capsys.readouterr().out

        assert "Unknown service 'unknown'" in output
        assert "Available services:" in output
        assert "devicemgmt" in output
        assert "media" in output

        commands.update_prompt.assert_not_called()

    def test_do_enter_service_without_required_arguments(self, capsys):
        """Verify missing required service arguments display usage information."""
        commands = create_commands()

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["events"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=["Reference"],
            ),
        ):
            commands.do_enter_service("events")

        output = capsys.readouterr().out

        assert "Service 'events' requires arguments" in output
        assert "Usage:" in output
        assert "Reference=<value>" in output
        assert "Example:" in output
        assert "Reference=$subscription" in output

        commands.update_prompt.assert_not_called()

    def test_do_enter_service_with_required_arguments(self):
        """Verify a service requiring arguments is entered successfully."""
        service = MagicMock()
        client = MagicMock()
        client.events.return_value = service

        commands = create_commands(client=client)

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["events"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=["Reference"],
            ),
            patch(
                "onvif.cli.interactive.navigation.parse_json_params",
                return_value={"Reference": "subscription-token"},
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_methods",
                return_value=["PullMessages", "Renew"],
            ),
        ):
            commands.do_enter_service('events {"Reference": "subscription-token"}')

        client.events.assert_called_once_with(Reference="subscription-token")

        assert commands.context.current_service is service
        assert commands.context.current_service_name == "events"
        commands.update_prompt.assert_called_once_with()

    def test_do_enter_service_without_required_arguments_uses_no_args(self):
        """Verify a service without required arguments is created without arguments."""
        service = MagicMock()
        client = MagicMock()
        client.devicemgmt.return_value = service

        commands = create_commands(client=client)

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["devicemgmt"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_methods",
                return_value=["GetDeviceInformation"],
            ),
        ):
            commands.do_enter_service("devicemgmt")

        client.devicemgmt.assert_called_once_with()

        assert commands.context.current_service is service
        assert commands.context.current_service_name == "devicemgmt"
        commands.update_prompt.assert_called_once_with()

    def test_do_enter_service_missing_required_argument(self, capsys):
        """Verify missing required arguments are reported."""
        commands = create_commands()

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["events"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=["Reference", "Mode"],
            ),
            patch(
                "onvif.cli.interactive.navigation.parse_json_params",
                return_value={"Reference": "subscription-token"},
            ),
        ):
            commands.do_enter_service('events {"Reference": "subscription-token"}')

        output = capsys.readouterr().out

        assert "Missing required arguments: Mode" in output
        assert "Usage:" in output
        assert "Reference=<value>" in output
        assert "Mode=<value>" in output

        commands.update_prompt.assert_not_called()

    def test_do_enter_service_parsing_error(self, capsys):
        """Verify invalid service arguments are reported."""
        commands = create_commands()

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["events"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=["Reference"],
            ),
            patch(
                "onvif.cli.interactive.navigation.parse_json_params",
                side_effect=ValueError("invalid JSON"),
            ),
        ):
            commands.do_enter_service("events invalid")

        output = capsys.readouterr().out

        assert "Error parsing arguments:" in output
        assert "invalid JSON" in output
        commands.update_prompt.assert_not_called()

    def test_do_enter_service_resolves_stored_reference(self):
        """Verify stored references are resolved before service creation."""
        service = MagicMock()
        client = MagicMock()
        client.events.return_value = service

        commands = create_commands(client=client)
        commands._resolve_stored_reference.return_value = "resolved-token"

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["events"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=["Reference"],
            ),
            patch(
                "onvif.cli.interactive.navigation.parse_json_params",
                return_value={"Reference": "$subscription"},
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_methods",
                return_value=["PullMessages"],
            ),
        ):
            commands.do_enter_service('events {"Reference": "$subscription"}')

        commands._resolve_stored_reference.assert_called_once_with("subscription")
        client.events.assert_called_once_with(Reference="resolved-token")

    def test_do_enter_service_unresolved_reference(self, capsys):
        """Verify unresolved stored references prevent service entry."""
        client = MagicMock()
        commands = create_commands(client=client)
        commands._resolve_stored_reference.return_value = None

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["events"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=["Reference"],
            ),
            patch(
                "onvif.cli.interactive.navigation.parse_json_params",
                return_value={"Reference": "$missing"},
            ),
        ):
            commands.do_enter_service('events {"Reference": "$missing"}')

        output = capsys.readouterr().out

        assert "Could not resolve reference '$missing'" in output
        client.events.assert_not_called()
        commands.update_prompt.assert_not_called()

    def test_do_enter_service_prints_method_preview(self, capsys):
        """Verify service methods are displayed after entering a service."""
        service = MagicMock()
        client = MagicMock()
        client.devicemgmt.return_value = service

        methods = ["Method1", "Method2", "Method3"]

        commands = create_commands(client=client)

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["devicemgmt"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_methods",
                return_value=methods,
            ),
        ):
            commands.do_enter_service("devicemgmt")

        output = strip_ansi(capsys.readouterr().out)

        assert "Entered service:" in output
        assert "devicemgmt" in output
        assert "Available methods:" in output
        assert "Method1" in output
        assert "Method2" in output
        assert "Method3" in output
        assert "Type up to exit service mode." in output

    def test_do_enter_service_prints_more_methods_message(self, capsys):
        """Verify more than ten methods display the truncated preview."""
        service = MagicMock()
        client = MagicMock()
        client.devicemgmt.return_value = service

        methods = [f"Method{i}" for i in range(15)]

        commands = create_commands(client=client)

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["devicemgmt"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_methods",
                return_value=methods,
            ),
        ):
            commands.do_enter_service("devicemgmt")

        output = capsys.readouterr().out

        assert "Method0" in output
        assert "Method9" in output
        assert "Method10" not in output
        assert "5 more." in output
        assert "TAB" in output

    def test_do_enter_service_handles_service_creation_error(self, capsys):
        """Verify service creation errors are reported."""
        client = MagicMock()
        client.devicemgmt.side_effect = RuntimeError("service unavailable")

        commands = create_commands(client=client)

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["devicemgmt"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=[],
            ),
        ):
            commands.do_enter_service("devicemgmt")

        output = capsys.readouterr().out

        assert "Error entering service:" in output
        assert "service unavailable" in output
        commands.update_prompt.assert_not_called()

    def test_do_enter_service_prints_traceback_in_debug_mode(self):
        """Verify service creation errors print a traceback in debug mode."""
        client = MagicMock()
        client.devicemgmt.side_effect = RuntimeError("service unavailable")

        commands = create_commands(client=client, debug=True)

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["devicemgmt"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.navigation.traceback.print_exc",
            ) as print_exc,
        ):
            commands.do_enter_service("devicemgmt")

        print_exc.assert_called_once_with()

    def test_do_enter_service_does_not_print_traceback_without_debug(
        self,
    ):
        """Verify service creation errors do not print a traceback without debug."""
        client = MagicMock()
        client.devicemgmt.side_effect = RuntimeError("service unavailable")

        commands = create_commands(client=client, debug=False)

        with (
            patch(
                "onvif.cli.interactive.navigation.get_device_available_services",
                return_value=["devicemgmt"],
            ),
            patch(
                "onvif.cli.interactive.navigation.get_service_required_args",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.navigation.traceback.print_exc",
            ) as print_exc,
        ):
            commands.do_enter_service("devicemgmt")

        print_exc.assert_not_called()


class TestNavigationCommandsExitService:
    """Test exit service alias."""

    def test_do_exit_service_delegates_to_do_up(self):
        """Verify exit_service is an alias for up."""
        commands = create_commands()

        with patch.object(commands, "do_up") as do_up:
            commands.do_exit_service("test")

        do_up.assert_called_once_with("test")
