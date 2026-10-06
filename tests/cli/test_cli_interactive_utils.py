# pylint: disable=protected-access
"""Tests for ONVIF interactive shell utilities."""

import socket
import ssl
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from onvif.cli.interactive.utils import ShellUtilities

from .conftest import strip_ansi


def create_args(**overrides):
    """Create mocked CLI arguments."""
    args = MagicMock()

    args.host = overrides.get("host", "192.168.1.100")
    args.port = overrides.get("port", 80)
    args.username = overrides.get("username", "admin")
    args.digest = overrides.get("digest", False)
    args.https = overrides.get("https", False)
    args.no_verify_ssl = overrides.get("no_verify_ssl", False)
    args.timeout = overrides.get("timeout", 10)
    args.debug = overrides.get("debug", False)
    args.no_patch = overrides.get("no_patch", False)
    args.wsdl = overrides.get("wsdl", None)
    args.health_check_interval = overrides.get("health_check_interval", 10)

    return args


def create_context(**overrides):
    """Create a mocked shell context for utility tests.

    Args:
        **overrides: Optional context values that should override defaults.

    Returns:
        A mock shell context configured with common test values.
    """
    context = MagicMock()
    context.args = create_args()
    context.client = MagicMock()
    context.current_service = None
    context.current_service_name = None
    context.base_commands = [
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

    for key, value in overrides.items():
        setattr(context, key, value)

    return context


def create_utilities():
    """Create a minimally initialized ``ShellUtilities`` instance.

    Returns:
        A shell utility instance with a mocked shell context.
    """
    utilities = ShellUtilities()
    utilities.context = create_context()
    utilities.stdout = MagicMock()
    return utilities


class TestShellUtilitiesInitialization:  # pylint: disable=too-few-public-methods
    """Test health-check initialization."""

    def test_initialize_health_check_creates_event(self):
        """Verify that health-check initialization creates a stop event."""
        utilities = create_utilities()

        with (
            patch("onvif.cli.interactive.utils.threading.Event") as event_cls,
            patch("onvif.cli.interactive.utils.threading.Thread") as thread_cls,
        ):
            utilities._initialize_health_check()

        event_cls.assert_called_once_with()
        assert utilities.stop_health_check is event_cls.return_value

        thread_cls.assert_called_once_with(
            target=utilities._periodic_health_check,
            daemon=True,
        )
        assert utilities.health_check_thread is thread_cls.return_value


class TestShellUtilitiesPrompt:
    """Test interactive shell prompt generation."""

    def test_updates_root_prompt(self):
        """Verify that the root prompt contains connection information."""
        utilities = create_utilities()

        utilities.update_prompt()

        assert utilities.prompt == "admin@192.168.1.100:80 > "

    def test_updates_service_prompt(self):
        """Verify that the service name is included in service mode."""
        utilities = create_utilities()
        utilities.context.current_service_name = "devicemgmt"

        utilities.update_prompt()

        assert utilities.prompt == "admin@192.168.1.100:80/devicemgmt > "


class TestShellUtilitiesDisplayGrid:
    """Test grid formatting and terminal display."""

    def test_display_grid_returns_without_output_for_empty_items(self):
        """Verify that an empty item list produces no output."""
        utilities = create_utilities()

        with patch("builtins.print") as print_mock:
            utilities._display_grid([])

        print_mock.assert_not_called()

    def test_display_grid_uses_terminal_width(self):
        """Verify that grid layout uses the detected terminal width."""
        utilities = create_utilities()

        with (
            patch(
                "onvif.cli.interactive.utils.get_device_available_services",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.utils.shutil.get_terminal_size",
                return_value=SimpleNamespace(columns=20),
            ),
            patch("builtins.print") as print_mock,
        ):
            utilities._display_grid(["one", "two", "three", "four"])

        assert print_mock.call_count > 0

    def test_display_grid_falls_back_to_default_width(self):
        """Verify that terminal-size failures use an 80-column fallback."""
        utilities = create_utilities()

        with (
            patch(
                "onvif.cli.interactive.utils.get_device_available_services",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.utils.shutil.get_terminal_size",
                side_effect=RuntimeError,
            ),
            patch("builtins.print") as print_mock,
        ):
            utilities._display_grid(["one", "two"])

        print_mock.assert_called_once_with("one  two")

    @pytest.mark.parametrize(
        "exception",
        [
            KeyError,
            ValueError,
            RuntimeError,
        ],
    )
    def test_display_grid_handles_terminal_size_errors(self, exception):
        """Verify that known terminal-size errors use the fallback width."""
        utilities = create_utilities()

        with (
            patch(
                "onvif.cli.interactive.utils.get_device_available_services",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.utils.shutil.get_terminal_size",
                side_effect=exception,
            ),
            patch("builtins.print") as print_mock,
        ):
            utilities._display_grid(["one", "two"])

        print_mock.assert_called()

    def test_display_grid_colors_device_services(self):
        """Verify that device services are displayed using service coloring."""
        utilities = create_utilities()

        with (
            patch(
                "onvif.cli.interactive.utils.get_device_available_services",
                return_value=["devicemgmt"],
            ),
            patch(
                "onvif.cli.interactive.utils.colorize",
                side_effect=lambda value, _color: f"<{value}>",
            ),
            patch(
                "onvif.cli.interactive.utils.shutil.get_terminal_size",
                return_value=SimpleNamespace(columns=80),
            ),
            patch("builtins.print") as print_mock,
        ):
            utilities._display_grid(["devicemgmt", "help"])

        output = print_mock.call_args.args[0]

        assert "<devicemgmt>" in output
        assert "help" in output

    def test_display_grid_does_not_query_services_in_service_mode(self):
        """Verify that root-level services are not queried in service mode."""
        utilities = create_utilities()
        utilities.context.current_service = MagicMock()

        with (
            patch(
                "onvif.cli.interactive.utils.get_device_available_services"
            ) as get_services,
            patch("builtins.print"),
        ):
            utilities._display_grid(["GetDeviceInformation"])

        get_services.assert_not_called()

    def test_columnize_delegates_to_display_grid(self):
        """Verify that ``columnize`` delegates to ``_display_grid``."""
        utilities = create_utilities()

        with patch.object(utilities, "_display_grid") as display_grid:
            utilities.columnize(["one", "two"], 40)

        display_grid.assert_called_once_with(["one", "two"])

    def test_columnize_returns_for_empty_list(self):
        """Verify that ``columnize`` ignores an empty list."""
        utilities = create_utilities()

        with patch.object(utilities, "_display_grid") as display_grid:
            result = utilities.columnize([])  # pylint: disable=assignment-from-none

        display_grid.assert_not_called()
        assert result is None


class TestShellUtilitiesPrintTopics:
    """Test command-topic display."""

    def test_print_topics_returns_for_empty_commands(self):
        """Verify that no output is produced for an empty command list."""
        utilities = create_utilities()

        with patch.object(utilities, "_display_grid") as display_grid:
            result = utilities.print_topics(  # pylint: disable=assignment-from-none
                "Commands", [], 10, 2
            )

        display_grid.assert_not_called()
        assert result is None

    def test_print_topics_writes_nonempty_header(self, capsys):
        """Verify that a nonempty header is printed to stdout."""
        utilities = create_utilities()

        with patch.object(utilities, "_display_grid") as display_grid:
            utilities.print_topics("Commands", ["help", "exit"], 10, 2)

        captured = capsys.readouterr()

        assert captured.out == "Commands\n\n"
        display_grid.assert_called_once_with(["help", "exit"])

    def test_print_topics_ignores_whitespace_header(self):
        """Verify that whitespace-only headers are not written."""
        utilities = create_utilities()

        with patch.object(utilities, "_display_grid") as display_grid:
            utilities.print_topics("   ", ["help"], 10, 2)

        utilities.stdout.write.assert_not_called()
        display_grid.assert_called_once_with(["help"])


class TestShellUtilitiesSuggestions:
    """Test command suggestion generation."""

    def test_get_suggestions_in_root_mode(self):
        """Verify that root suggestions include matching services and commands."""
        utilities = create_utilities()

        with (
            patch(
                "onvif.cli.interactive.utils.get_device_available_services",
                return_value=["devicemgmt", "media", "events"],
            ),
            patch(
                "onvif.cli.interactive.utils.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            suggestions = utilities.get_suggestions("me")

        assert suggestions == ["media"]

    def test_get_suggestions_includes_root_commands(self):
        """Verify that matching root commands are returned."""
        utilities = create_utilities()

        with (
            patch(
                "onvif.cli.interactive.utils.get_device_available_services",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.utils.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            suggestions = utilities.get_suggestions("hel")  # codespell:ignore

        assert suggestions == ["help"]

    def test_get_suggestions_is_case_insensitive(self):
        """Verify that suggestion matching ignores case."""
        utilities = create_utilities()

        with patch(
            "onvif.cli.interactive.utils.get_device_available_services",
            return_value=["Media"],
        ):
            suggestions = utilities.get_suggestions("med")

        assert [strip_ansi(item) for item in suggestions] == ["Media"]

    def test_get_suggestions_in_service_mode(self):
        """Verify that service methods are suggested in service mode."""
        utilities = create_utilities()
        utilities.context.current_service = MagicMock()

        with (
            patch(
                "onvif.cli.interactive.utils.get_service_methods",
                return_value=["GetProfiles", "GetStreamUri", "GetStatus"],
            ),
            patch(
                "onvif.cli.interactive.utils.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            suggestions = utilities.get_suggestions("getp")

        assert suggestions == ["GetProfiles"]

    def test_get_suggestions_includes_service_helpers(self):
        """Verify that ``type`` and ``desc`` are available in service mode."""
        utilities = create_utilities()
        utilities.context.current_service = MagicMock()

        with (
            patch(
                "onvif.cli.interactive.utils.get_service_methods",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.utils.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            suggestions = utilities.get_suggestions("d")

        assert suggestions == ["desc"]

    def test_get_suggestions_limits_results_to_five(self):
        """Verify that suggestions are limited to five results."""
        utilities = create_utilities()

        with (
            patch(
                "onvif.cli.interactive.utils.get_device_available_services",
                return_value=[
                    "service1",
                    "service2",
                    "service3",
                    "service4",
                    "service5",
                    "service6",
                ],
            ),
            patch(
                "onvif.cli.interactive.utils.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            suggestions = utilities.get_suggestions("service")

        assert len(suggestions) == 5


class TestShellUtilitiesCompletion:
    """Test command-name tab completion."""

    def test_completenames_in_root_mode(self):
        """Verify that root completion includes services and base commands."""
        utilities = create_utilities()

        with patch(
            "onvif.cli.interactive.utils.get_device_available_services",
            return_value=["devicemgmt", "media"],
        ):
            completions = utilities.completenames("me")

        assert completions == ["media"]

    def test_completenames_includes_root_commands(self):
        """Verify that root completion includes matching base commands."""
        utilities = create_utilities()

        with patch(
            "onvif.cli.interactive.utils.get_device_available_services",
            return_value=[],
        ):
            completions = utilities.completenames("hel")  # codespell:ignore

        assert completions == ["help"]

    def test_completenames_in_service_mode(self):
        """Verify that service methods are completed."""
        utilities = create_utilities()
        utilities.context.current_service = MagicMock()

        with (
            patch(
                "onvif.cli.interactive.utils.get_service_methods",
                return_value=["GetProfiles", "GetStreamUri"],
            ),
            patch(
                "onvif.cli.interactive.utils.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            completions = utilities.completenames("getp")

        assert completions == ["GetProfiles"]

    def test_completenames_includes_service_helpers(self):
        """Verify that service helper commands are available for completion."""
        utilities = create_utilities()
        utilities.context.current_service = MagicMock()

        with (
            patch(
                "onvif.cli.interactive.utils.get_service_methods",
                return_value=[],
            ),
            patch(
                "onvif.cli.interactive.utils.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            completions = utilities.completenames("d")

        assert completions == ["desc"]

    def test_completenames_is_case_insensitive(self):
        """Verify that completion matching ignores case."""
        utilities = create_utilities()

        with patch(
            "onvif.cli.interactive.utils.get_device_available_services",
            return_value=["Media"],
        ):
            completions = utilities.completenames("med")

        assert completions == ["Media"]


class TestShellUtilitiesHealthCheck:
    """Test periodic device connection health checks."""

    def _configure_health_check(self, utilities, **args):
        """Configure health-check context and mocked stop event."""
        utilities.context.args = create_args(**args)
        utilities.stop_health_check = MagicMock()

    def test_waits_before_first_health_check(self):
        """Verify that the first health check waits for the configured interval."""
        utilities = create_utilities()
        self._configure_health_check(utilities, health_check_interval=15)

        utilities.stop_health_check.wait.side_effect = [
            None,
            None,
        ]
        utilities.stop_health_check.is_set.side_effect = [
            True,
        ]

        utilities._periodic_health_check()

        utilities.stop_health_check.wait.assert_called_once_with(15)

    def test_uses_default_health_check_interval(self):
        """Verify that the default health-check interval is ten seconds."""
        utilities = create_utilities()
        utilities.context.args = SimpleNamespace(
            host="192.168.1.100",
            port=80,
            https=False,
        )
        utilities.stop_health_check = MagicMock()
        utilities.stop_health_check.is_set.return_value = True

        utilities._periodic_health_check()

        utilities.stop_health_check.wait.assert_called_once_with(10)

    def test_successful_http_health_check(self):
        """Verify that a successful HTTP health check creates and closes a socket."""
        utilities = create_utilities()
        self._configure_health_check(
            utilities,
            https=False,
            health_check_interval=10,
        )

        utilities.stop_health_check.is_set.side_effect = [
            False,
            True,
        ]

        socket_mock = MagicMock()

        with patch(
            "onvif.cli.interactive.utils.socket.create_connection",
            return_value=socket_mock,
        ) as create_connection:
            utilities._periodic_health_check()

        create_connection.assert_called_once_with(
            ("192.168.1.100", 80),
            timeout=5.0,
        )
        socket_mock.close.assert_called_once_with()

    def test_successful_https_health_check(self):
        """Verify that HTTPS health checks create a TLS socket."""
        utilities = create_utilities()
        self._configure_health_check(
            utilities,
            https=True,
            port=443,
            health_check_interval=10,
        )

        utilities.stop_health_check.is_set.side_effect = [
            False,
            True,
        ]

        raw_socket = MagicMock()
        tls_socket = MagicMock()

        ssl_context = MagicMock()
        ssl_context.wrap_socket.return_value = tls_socket

        with (
            # pylint: disable=redefined-outer-name
            patch(
                "onvif.cli.interactive.utils.ssl.create_default_context",
                return_value=ssl_context,
            ) as create_context,
            patch(
                "onvif.cli.interactive.utils.socket.socket",
                return_value=raw_socket,
            ) as socket_cls,
        ):
            utilities._periodic_health_check()

        create_context.assert_called_once_with()
        socket_cls.assert_called_once_with(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        assert ssl_context.minimum_version == ssl.TLSVersion.TLSv1_2
        assert ssl_context.check_hostname is False
        assert ssl_context.verify_mode == ssl.CERT_NONE

        ssl_context.wrap_socket.assert_called_once_with(
            raw_socket,
            server_hostname="192.168.1.100",
        )
        tls_socket.settimeout.assert_called_once_with(5.0)
        tls_socket.connect.assert_called_once_with(("192.168.1.100", 443))
        tls_socket.close.assert_called_once_with()

    @pytest.mark.parametrize(
        "exception",
        [
            socket.timeout("timed out"),
            ConnectionRefusedError("connection refused"),
            socket.gaierror("name resolution failed"),
            ssl.SSLError("TLS failed"),
            ssl.SSLEOFError("TLS EOF"),
            OSError("socket failure"),
        ],
    )
    def test_http_health_check_exits_on_connection_failure(
        self,
        exception,
        capsys,
    ):
        """Verify that connection failures terminate the interactive shell."""
        utilities = create_utilities()
        self._configure_health_check(
            utilities,
            https=False,
            health_check_interval=10,
        )

        utilities.stop_health_check.is_set.return_value = False

        with (
            patch(
                "onvif.cli.interactive.utils.socket.create_connection",
                side_effect=exception,
            ),
            patch(
                "onvif.cli.interactive.utils.os._exit",
                side_effect=SystemExit(1),
            ) as exit_mock,
        ):
            with pytest.raises(SystemExit, match="1"):
                utilities._periodic_health_check()

        exit_mock.assert_called_once_with(1)

        captured = capsys.readouterr()

        assert "Connection to device lost." in captured.err
        assert "Health check failed:" in captured.err
        assert "Exiting ONVIF interactive shell..." in captured.err

    def test_health_check_closes_socket_after_success(self):
        """Verify that sockets are closed after a successful health check."""
        utilities = create_utilities()
        self._configure_health_check(utilities)

        utilities.stop_health_check.is_set.side_effect = [
            False,
            True,
        ]

        socket_mock = MagicMock()

        with patch(
            "onvif.cli.interactive.utils.socket.create_connection",
            return_value=socket_mock,
        ):
            utilities._periodic_health_check()

        socket_mock.close.assert_called_once_with()


class TestShellUtilitiesConnectionError:
    """Test interactive shell connection-error handling."""

    def test_handle_connection_error_prints_messages(self, capsys):
        """Verify that connection errors produce user-facing messages."""
        utilities = create_utilities()

        with (
            patch(
                "onvif.cli.interactive.utils.sys.exit",
                side_effect=SystemExit(1),
            ) as exit_mock,
        ):
            with pytest.raises(SystemExit, match="1"):
                utilities._handle_connection_error()

        exit_mock.assert_called_once_with(1)

        captured = capsys.readouterr()

        assert "Connection to device lost." in captured.err
        assert "Exiting ONVIF interactive shell..." in captured.err
        assert "Goodbye!" in captured.err

    def test_handle_connection_error_prints_traceback_in_debug_mode(
        self,
        capsys,
    ):
        """Verify that debug mode prints the current exception traceback."""
        utilities = create_utilities()
        utilities.context.args.debug = True

        with (
            patch("onvif.cli.interactive.utils.traceback.print_exc") as print_exc,
            patch(
                "onvif.cli.interactive.utils.sys.exit",
                side_effect=SystemExit(1),
            ),
        ):
            with pytest.raises(SystemExit, match="1"):
                utilities._handle_connection_error()

        print_exc.assert_called_once_with()

        captured = capsys.readouterr()

        assert "Connection to device lost." in captured.err

    def test_handle_connection_error_does_not_print_traceback_without_debug(
        self,
    ):
        """Verify that traceback output is skipped when debug mode is disabled."""
        utilities = create_utilities()
        utilities.context.args.debug = False

        with (
            patch("onvif.cli.interactive.utils.traceback.print_exc") as print_exc,
            patch(
                "onvif.cli.interactive.utils.sys.exit",
                side_effect=SystemExit(1),
            ),
        ):
            with pytest.raises(SystemExit, match="1"):
                utilities._handle_connection_error()

        print_exc.assert_not_called()


class TestShellUtilitiesSplitCommands:
    """Test multi-command string parsing."""

    @pytest.fixture
    def utilities(self):
        """Provide a shell utility instance for command parsing."""
        return create_utilities()

    @pytest.mark.parametrize(
        ("command", "expected"),
        [
            (
                "first && second",
                ["first", "second"],
            ),
            (
                "first && second && third",
                ["first", "second", "third"],
            ),
            (
                "  first   &&   second  ",
                ["first", "second"],
            ),
            (
                "single command",
                ["single command"],
            ),
            (
                "",
                [],
            ),
            (
                "   ",
                [],
            ),
        ],
    )
    def test_splits_top_level_commands(self, utilities, command, expected):
        """Verify that top-level ``&&`` separators split commands."""
        assert utilities._split_multi_commands(command) == expected

    @pytest.mark.parametrize(
        "command",
        [
            "first && 'second && third'",
            'first && "second && third"',
            'first && {"value": "a && b"}',
            'first && ["a && b"]',
            "first && (a && b)",
        ],
    )
    def test_ignores_separators_inside_structures(self, utilities, command):
        """Verify that ``&&`` inside quotes or brackets is preserved."""
        result = utilities._split_multi_commands(command)

        assert len(result) == 2
        assert result[0] == "first"
        assert "&&" in result[1]

    def test_preserves_quotes(self, utilities):
        """Verify that quote characters remain in command arguments."""
        command = 'first "value && preserved" && second'

        result = utilities._split_multi_commands(command)

        assert result == [
            'first "value && preserved"',
            "second",
        ]

    def test_handles_nested_brackets(self, utilities):
        """Verify that nested bracket structures do not split commands."""
        command = 'first {"a": [1, {"b": "x && y"}]} && second'

        result = utilities._split_multi_commands(command)

        assert result == [
            'first {"a": [1, {"b": "x && y"}]}',
            "second",
        ]

    def test_handles_unbalanced_closing_brackets(self, utilities):
        """Verify that bracket depth never becomes negative."""
        command = "first } && second"

        result = utilities._split_multi_commands(command)

        assert result == [
            "first }",
            "second",
        ]

    def test_ignores_ampersands_that_are_not_double(self, utilities):
        """Verify that single ampersands are not treated as separators."""
        command = "first & second"

        result = utilities._split_multi_commands(command)

        assert result == ["first & second"]

    def test_ignores_trailing_empty_commands(self, utilities):
        """Verify that trailing separators do not create empty commands."""
        command = "first &&"

        result = utilities._split_multi_commands(command)

        assert result == ["first"]

    def test_ignores_multiple_spaces_after_separator(self, utilities):
        """Verify that spaces after separators are removed."""
        command = "first &&     second"

        result = utilities._split_multi_commands(command)

        assert result == ["first", "second"]
