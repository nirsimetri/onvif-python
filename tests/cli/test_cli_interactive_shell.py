# pylint: disable=protected-access
"""Tests for the ONVIF interactive shell."""

import cmd
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import RequestException

from onvif.cli.interactive.shell import InteractiveShell
from onvif.utils.exceptions import ONVIFOperationException

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


def create_client():
    """Create a mock ONVIF client with the responses required by the shell.

    Returns:
        A mock ONVIF client configured with basic device information and
        supported ONVIF version information.
    """
    client = MagicMock()

    device_service = MagicMock()
    device_service.GetDeviceInformation.return_value = SimpleNamespace(
        Manufacturer="Dahua",
        Model="DH-H5D-5F",
        FirmwareVersion="2.860.0000000.26.R",
        SerialNumber="AM08C90PAG3C79B",
        HardwareId="1.00",
    )
    device_service.GetCapabilities.return_value = {
        "Device": {
            "System": {
                "SupportedVersions": [
                    SimpleNamespace(Major=2, Minor=0),
                    SimpleNamespace(Major=2, Minor=5),
                    SimpleNamespace(Major=2, Minor=6),
                ]
            }
        }
    }

    client.devicemgmt.return_value = device_service

    return client


def create_device_data():
    """Create device information data as dict."""

    return {
        "Manufacturer": "Dahua",
        "Model": "DH-H5D-5F",
        "FirmwareVersion": "2.860.0000000.26.R",
        "SerialNumber": "AM08C90PAG3C79B",
        "HardwareId": "1.00",
    }


class TestInteractiveShellInitialization:
    """Test initialization and startup behavior of ``InteractiveShell``."""

    @pytest.fixture
    def client(self):
        """Provide a mocked ONVIF client for initialization tests."""
        return create_client()

    @pytest.fixture
    def args(self):
        """Provide default CLI arguments for initialization tests."""
        return create_args()

    @pytest.fixture
    def device_data(self):
        """Provide default device info for initialization tests."""
        return create_device_data()

    @staticmethod
    def _create_shell(client, args, device_data):
        with patch("onvif.cli.interactive.utils.threading.Thread"):
            return InteractiveShell(client, args, device_data)

    def test_initializes_context(self, client, args, device_data):
        """Verify that initialization creates the shared shell context."""
        shell = self._create_shell(client, args, device_data)

        assert shell.context.client is client
        assert shell.context.args is args

    def test_initializes_cmd_state(self, client, args, device_data):
        """Verify that ``cmd.Cmd`` state is initialized."""
        shell = self._create_shell(client, args, device_data)

        assert hasattr(shell, "stdin")
        assert hasattr(shell, "stdout")
        assert hasattr(shell, "cmdqueue")
        assert shell.prompt.endswith("> ")

    def test_uses_provided_device_information(self, client, args, device_data):
        """Verify that provided device information is used during initialization."""
        shell = self._create_shell(client, args, device_data)

        assert "Dahua" in shell.context.device_info_text
        assert "DH-H5D-5F" in shell.context.device_info_text
        assert "2.860.0000000.26.R" in shell.context.device_info_text
        assert "AM08C90PAG3C79B" in shell.context.device_info_text
        assert "1.00" in shell.context.device_info_text

    def test_fetches_supported_onvif_versions(self, client, args, device_data):
        """Verify that supported ONVIF versions are requested during initialization."""
        self._create_shell(client, args, device_data)

        client.devicemgmt.return_value.GetCapabilities.assert_called_once_with(
            Category="All"
        )

    def test_builds_device_information_text(self, client, args, device_data):
        """Verify that device information is formatted into the shell context."""
        shell = self._create_shell(client, args, device_data)

        assert shell.context.device_info_text is not None
        assert "Dahua" in shell.context.device_info_text
        assert "DH-H5D-5F" in shell.context.device_info_text
        assert "2.860.0000000.26.R" in shell.context.device_info_text
        assert "AM08C90PAG3C79B" in shell.context.device_info_text
        assert "1.00" in shell.context.device_info_text
        assert "2.06" in shell.context.device_info_text

    def test_prints_intro_with_device_information(self, client, args, device_data):
        """Verify that the interactive intro receives formatted device information."""
        with patch(
            "onvif.cli.interactive.shell.print_interactive_intro",
            return_value="Interactive ONVIF shell",
        ) as print_intro:
            shell = self._create_shell(client, args, device_data)

        print_intro.assert_called_once_with(
            args,
            shell.context.device_info_text,
        )
        assert shell.intro == "Interactive ONVIF shell"

    def test_starts_health_check_after_initialization(self, client, args, device_data):
        """Verify that the background health-check thread starts after initialization."""
        with patch("onvif.cli.interactive.utils.threading.Thread") as thread_cls:
            health_thread = thread_cls.return_value

            InteractiveShell(client, args, device_data)

        health_thread.start.assert_called_once_with()

    def test_handles_missing_capabilities(self, client, args, device_data):
        """Verify that initialization continues when capability data is unavailable."""
        client.devicemgmt.return_value.GetCapabilities.side_effect = KeyError(
            "SupportedVersions"
        )

        shell = self._create_shell(client, args, device_data)

        assert shell.context.device_info_text is not None
        assert "Dahua" in shell.context.device_info_text
        assert "ONVIF Version" in shell.context.device_info_text

    def test_handles_missing_device_attributes(self, client, args):
        """Verify that missing device attributes fall back to ``Unknown``."""
        device_data = {}

        shell = self._create_shell(client, args, device_data)

        output = strip_ansi(shell.context.device_info_text)

        assert "Manufacturer  : Unknown" in output
        assert "Model         : Unknown" in output
        assert "Firmware      : Unknown" in output
        assert "Serial        : Unknown" in output
        assert "HardwareId    : Unknown" in output

    def test_handles_connection_error(self, client, args, device_data):
        """Verify that transport-related ONVIF errors invoke connection handling."""
        original_exception = RequestException("Connection failed")

        client.devicemgmt.return_value.GetCapabilities.side_effect = (
            ONVIFOperationException(
                "Connection failed",
                original_exception=original_exception,
            )
        )

        with patch.object(
            InteractiveShell,
            "_handle_connection_error",
        ) as handle_connection_error:
            shell = self._create_shell(client, args, device_data)

        handle_connection_error.assert_called_once_with()
        assert "ONVIF Version" in shell.context.device_info_text
        assert "Unknown" in shell.context.device_info_text


class TestInteractiveShellDeviceInformation:
    """Test device information formatting."""

    def test_formats_complete_device_information(self):
        """Verify that all device information fields are formatted."""
        shell = object.__new__(InteractiveShell)

        device_data = {
            "Manufacturer": "Dahua",
            "Model": "DH-H5D-5F",
            "FirmwareVersion": "2.860",
            "SerialNumber": "ABC123",
            "HardwareId": "1.00",
        }

        result = shell._format_device_information(device_data)

        assert result == {
            "manufacturer": "Dahua",
            "model": "DH-H5D-5F",
            "firmware": "2.860",
            "serial": "ABC123",
            "hardware_id": "1.00",
        }

    def test_formats_missing_device_information(self):
        """Verify that missing fields fall back to ``Unknown``."""
        shell = object.__new__(InteractiveShell)

        result = shell._format_device_information({})

        assert result == {
            "manufacturer": "Unknown",
            "model": "Unknown",
            "firmware": "Unknown",
            "serial": "Unknown",
            "hardware_id": "Unknown",
        }

    def test_handles_invalid_device_information(self):
        """Verify that invalid device data falls back to ``Unknown``."""
        shell = object.__new__(InteractiveShell)

        class InvalidDeviceData:
            """Device data that raises an error when accessed."""

            def get(self, _key, _default):
                """ "Get invalid device data."""
                raise ValueError("Invalid device data")

        result = shell._format_device_information(InvalidDeviceData())

        assert result == {
            "manufacturer": "Unknown",
            "model": "Unknown",
            "firmware": "Unknown",
            "serial": "Unknown",
            "hardware_id": "Unknown",
        }


class TestInteractiveShellONVIFVersion:
    """Test ONVIF version detection and formatting."""

    @staticmethod
    def _create_shell(client):
        shell = object.__new__(InteractiveShell)
        shell.context = MagicMock()
        shell.context.client = client
        return shell

    def test_returns_unknown_when_capabilities_raise_onvif_error(self):
        """Verify that ONVIF operation errors return ``Unknown``."""
        client = MagicMock()
        client.devicemgmt.return_value.GetCapabilities.side_effect = (
            ONVIFOperationException(
                "Failed to get capabilities", RuntimeError("Failed")
            )
        )

        shell = self._create_shell(client)

        assert shell._get_onvif_version() == "Unknown"

    def test_handles_transport_error_from_onvif_error(self):
        """Verify that transport errors invoke connection handling."""
        client = MagicMock()

        original_exception = RequestException("Connection failed")

        client.devicemgmt.return_value.GetCapabilities.side_effect = (
            ONVIFOperationException(
                "Failed to get capabilities",
                original_exception=original_exception,
            )
        )

        shell = self._create_shell(client)

        with patch.object(
            shell,
            "_handle_connection_error",
        ) as handle_connection_error:
            result = shell._get_onvif_version()

        assert result == "Unknown"
        handle_connection_error.assert_called_once_with()

    def test_returns_unknown_for_empty_supported_versions(self):
        """Verify that an empty version list returns ``Unknown``."""
        client = MagicMock()
        client.devicemgmt.return_value.GetCapabilities.return_value = {
            "Device": {
                "System": {
                    "SupportedVersions": [],
                }
            }
        }

        shell = self._create_shell(client)

        assert shell._get_onvif_version() == "Unknown"

    def test_formats_version_without_minor(self):
        """Verify that versions without a minor component use the major version."""
        client = MagicMock()
        client.devicemgmt.return_value.GetCapabilities.return_value = {
            "Device": {
                "System": {
                    "SupportedVersions": [
                        SimpleNamespace(Major=3, Minor=None),
                    ]
                }
            }
        }

        shell = self._create_shell(client)

        assert shell._get_onvif_version() == "3"

    def test_returns_unknown_when_major_is_missing(self):
        """Verify that a version without a major component returns ``Unknown``."""
        client = MagicMock()
        client.devicemgmt.return_value.GetCapabilities.return_value = {
            "Device": {
                "System": {
                    "SupportedVersions": [
                        SimpleNamespace(Major=None, Minor=5),
                    ]
                }
            }
        }

        shell = self._create_shell(client)

        assert shell._get_onvif_version() == "Unknown"

    def test_formats_version_with_release_date(self):
        """Verify that a known ONVIF version includes its release date."""
        client = MagicMock()
        client.devicemgmt.return_value.GetCapabilities.return_value = {
            "Device": {
                "System": {
                    "SupportedVersions": [
                        SimpleNamespace(Major=2, Minor=60),
                    ]
                }
            }
        }

        shell = self._create_shell(client)

        with patch.object(
            shell,
            "_is_latest_released_version",
            return_value=False,
        ):
            result = shell._get_onvif_version()

        assert result.startswith("2.60 (")
        assert "[Latest]" not in result

    def test_formats_latest_version(self):
        """Verify that the latest released version includes the latest marker."""
        client = MagicMock()
        client.devicemgmt.return_value.GetCapabilities.return_value = {
            "Device": {
                "System": {
                    "SupportedVersions": [
                        SimpleNamespace(Major=2, Minor=60),
                    ]
                }
            }
        }

        shell = self._create_shell(client)

        with patch.object(
            shell,
            "_is_latest_released_version",
            return_value=True,
        ):
            result = shell._get_onvif_version()

        assert result.startswith("2.60 (")
        assert "[Latest]" in result

    def test_formats_unknown_version_without_release_date(self):
        """Verify that an unknown ONVIF version has no release-date suffix."""
        client = MagicMock()
        client.devicemgmt.return_value.GetCapabilities.return_value = {
            "Device": {
                "System": {
                    "SupportedVersions": [
                        SimpleNamespace(Major=9, Minor=99),
                    ]
                }
            }
        }

        shell = self._create_shell(client)

        assert shell._get_onvif_version() == "9.99"

    def test_selects_highest_supported_version(self):
        """Verify that the highest major/minor version is selected."""
        client = MagicMock()
        client.devicemgmt.return_value.GetCapabilities.return_value = {
            "Device": {
                "System": {
                    "SupportedVersions": [
                        SimpleNamespace(Major=2, Minor=0),
                        SimpleNamespace(Major=1, Minor=99),
                        SimpleNamespace(Major=2, Minor=6),
                        SimpleNamespace(Major=2, Minor=5),
                    ]
                }
            }
        }

        shell = self._create_shell(client)

        with patch.object(
            shell,
            "_is_latest_released_version",
            return_value=False,
        ):
            result = shell._get_onvif_version()

        assert result.startswith("2.06")


class TestInteractiveShellLatestVersion:
    """Test latest released ONVIF version detection."""

    def test_returns_true_for_latest_released_version(self):
        """Verify that the latest released version is detected."""
        shell = object.__new__(InteractiveShell)

        with patch(
            "onvif.cli.interactive.shell.date",
            wraps=date,
        ) as mock_date:
            mock_date.today.return_value = date(2026, 10, 6)

            assert shell._is_latest_released_version(date(2026, 6, 1))

    def test_returns_false_for_older_released_version(self):
        """Verify that an older released version is not considered latest."""
        shell = object.__new__(InteractiveShell)

        with patch(
            "onvif.cli.interactive.shell.ONVIF_VERSION_MAP",
            {
                (2, 5): date(2025, 1, 1),
                (2, 6): date(2026, 6, 1),
            },
        ):
            with patch("onvif.cli.interactive.shell.date") as mock_date:
                mock_date.today.return_value = date(2026, 10, 6)

                assert not shell._is_latest_released_version(date(2025, 1, 1))

    def test_returns_false_for_future_release(self):
        """Verify that a future release is not considered the latest."""
        shell = object.__new__(InteractiveShell)

        with patch("onvif.cli.interactive.shell.date") as mock_date:
            mock_date.today.return_value = date(2026, 10, 6)

            assert not shell._is_latest_released_version(date(2026, 12, 1))

    def test_returns_false_when_no_version_has_been_released(self):
        """Verify that no released versions results in ``False``."""
        shell = object.__new__(InteractiveShell)

        with patch(
            "onvif.cli.interactive.shell.ONVIF_VERSION_MAP",
            {
                (2, 7): date(2027, 1, 1),
            },
        ):
            with patch("onvif.cli.interactive.shell.date") as mock_date:
                mock_date.today.return_value = date(2026, 10, 6)

                assert not shell._is_latest_released_version(date(2027, 1, 1))

    def test_returns_true_for_december_release(self):
        """Verify that the December release is latest in December."""
        shell = object.__new__(InteractiveShell)

        with patch(
            "onvif.cli.interactive.shell.date",
            wraps=date,
        ) as mock_date:
            mock_date.today.return_value = date(2026, 12, 1)

            assert shell._is_latest_released_version(date(2026, 12, 1))

    def test_returns_true_for_june_release(self):
        """Verify that the June release is latest from June through November."""
        shell = object.__new__(InteractiveShell)

        with patch(
            "onvif.cli.interactive.shell.date",
            wraps=date,
        ) as mock_date:
            mock_date.today.return_value = date(2026, 10, 6)

            assert shell._is_latest_released_version(date(2026, 6, 1))

    def test_returns_true_for_previous_december_release(self):
        """Verify that the previous December release is latest before June."""
        shell = object.__new__(InteractiveShell)

        with patch(
            "onvif.cli.interactive.shell.date",
            wraps=date,
        ) as mock_date:
            mock_date.today.return_value = date(2026, 3, 1)

            assert shell._is_latest_released_version(date(2025, 12, 1))


class TestInteractiveShellPrompt:
    """Test prompt management for ``InteractiveShell``."""

    @pytest.fixture
    def shell(self):
        """Create a minimally initialized shell for prompt tests."""
        shell = object.__new__(InteractiveShell)
        cmd.Cmd.__init__(shell)
        shell.context = MagicMock()
        shell.context.args = create_args()
        shell.context.current_service_name = None
        return shell

    def test_updates_root_prompt(self, shell):
        """Verify that the prompt identifies the connected device in root mode."""
        shell.update_prompt()

        assert shell.prompt == "admin@192.168.1.100:80 > "

    def test_updates_service_prompt(self, shell):
        """Verify that the prompt includes the active service name."""
        shell.context.current_service_name = "devicemgmt"

        shell.update_prompt()

        assert shell.prompt == "admin@192.168.1.100:80/devicemgmt > "


class TestInteractiveShellCmdloop:
    """Test the customized command-loop implementation."""

    @pytest.fixture
    def shell(self):
        """Create a minimally initialized shell for command-loop tests."""
        shell = object.__new__(InteractiveShell)
        cmd.Cmd.__init__(shell)
        shell.prompt = "test > "
        shell.intro = None
        return shell

    def test_cmdloop_uses_intro(self, shell):
        """Verify that an explicitly supplied intro is written to stdout."""
        shell.cmdqueue = ["exit"]

        with (
            patch.object(shell, "onecmd", return_value=True),
            patch.object(shell.stdout, "write") as write,
        ):
            shell.cmdloop("Test intro")

        assert shell.intro == "Test intro"
        write.assert_called_once_with("Test intro\n")

    def test_cmdloop_processes_command_queue(self, shell):
        """Verify that queued commands are processed without reading stdin."""
        shell.cmdqueue = ["test"]

        with patch.object(
            shell,
            "onecmd",
            return_value=True,
        ) as onecmd:
            shell.cmdloop()

        onecmd.assert_called_once_with("test")

    def test_cmdloop_handles_eof(self, shell):
        """Verify that EOF is converted into the ``EOF`` command."""
        shell.cmdqueue = []

        with (
            patch(
                "builtins.input",
                side_effect=EOFError,
            ),
            patch.object(
                shell,
                "onecmd",
                return_value=True,
            ) as onecmd,
        ):
            shell.cmdloop()

        onecmd.assert_called_once_with("EOF")

    def test_cmdloop_handles_keyboard_interrupt(self, shell, capsys):
        """Verify that Ctrl-C produces an empty command instead of terminating."""
        shell.cmdqueue = []

        with (
            patch(
                "builtins.input",
                side_effect=KeyboardInterrupt,
            ),
            patch.object(
                shell,
                "onecmd",
                return_value=True,
            ) as onecmd,
        ):
            shell.cmdloop()

        onecmd.assert_called_once_with("")
        assert "^C" in capsys.readouterr().out


class TestInteractiveShellOnecmd:
    """Test command dispatch performed by ``InteractiveShell.onecmd``."""

    @pytest.fixture
    def shell(self):
        """Create a minimally initialized shell for command-dispatch tests."""
        shell = object.__new__(InteractiveShell)
        cmd.Cmd.__init__(shell)
        shell.context = MagicMock()
        shell.context.current_service = None
        return shell

    def test_empty_command_calls_emptyline(self, shell):
        """Verify that an empty command is delegated to ``emptyline``."""
        with patch.object(shell, "emptyline", return_value=None) as emptyline:
            result = shell.onecmd("   ")

        emptyline.assert_called_once_with()
        assert result is None

    def test_splits_chained_commands(self, shell):
        """Verify that commands separated by ``&&`` are executed independently."""
        shell._split_multi_commands = MagicMock(
            return_value=["first", "second", "third"]
        )
        shell.onecmd = MagicMock(side_effect=[None, None, None])

        # Call the real implementation rather than the mocked recursive method.
        # pylint: disable=no-value-for-parameter
        real_onecmd = InteractiveShell.onecmd.__get__(shell)

        result = real_onecmd("first && second && third")

        shell._split_multi_commands.assert_called_once_with("first && second && third")
        assert result is None
        assert shell.onecmd.call_count == 3

    def test_stops_chained_commands_when_command_requests_exit(self, shell):
        """Verify that command chaining stops when a command returns a stop value."""
        shell._split_multi_commands = MagicMock(return_value=["first", "exit", "third"])
        shell.onecmd = MagicMock(side_effect=[None, True])

        # pylint: disable=no-value-for-parameter
        real_onecmd = InteractiveShell.onecmd.__get__(shell)

        result = real_onecmd("first && exit && third")

        assert result is True
        assert shell.onecmd.call_count == 2

    def test_delegates_root_command_to_cmd(self, shell):
        """Verify that normal root commands use ``cmd.Cmd`` dispatch."""
        with patch.object(
            cmd.Cmd,
            "onecmd",
            return_value=None,
        ) as cmd_onecmd:
            result = InteractiveShell.onecmd(shell, "help")

        cmd_onecmd.assert_called_once_with("help")
        assert result is None

    def test_dispatches_service_method_in_service_mode(self, shell):
        """Verify that unknown commands in service mode use the shell fallback."""
        shell.context.current_service = MagicMock()

        with patch.object(
            shell,
            "default",
            return_value=None,
        ) as default:
            result = InteractiveShell.onecmd(shell, "GetDeviceInformation")

        default.assert_called_once_with("GetDeviceInformation")
        assert result is None


class TestInteractiveShellDefault:
    """Test fallback handling for unknown commands."""

    @pytest.fixture
    def shell(self):
        """Create a minimally initialized shell for default-command tests."""
        shell = object.__new__(InteractiveShell)
        cmd.Cmd.__init__(shell)
        shell.context = MagicMock()
        shell.context.current_service = None
        return shell

    def test_enters_known_service(self, shell):
        """Verify that a known service name enters service mode."""
        with (
            patch(
                "onvif.cli.interactive.shell.get_device_available_services",
                return_value=["devicemgmt", "media"],
            ),
            patch.object(
                shell,
                "do_enter_service",
                return_value=None,
            ) as enter_service,
        ):
            shell.default("devicemgmt")

        enter_service.assert_called_once_with("devicemgmt")

    def test_enters_service_with_arguments(self, shell):
        """Verify that a service name followed by arguments enters that service."""
        with (
            patch(
                "onvif.cli.interactive.shell.get_device_available_services",
                return_value=["subscription"],
            ),
            patch.object(
                shell,
                "do_enter_service",
                return_value=None,
            ) as enter_service,
        ):
            shell.default("subscription Name=$subscription")

        enter_service.assert_called_once_with("subscription Name=$subscription")

    def test_executes_service_method_without_arguments(self, shell):
        """Verify that a service method without parameters is executed."""
        shell.context.current_service = MagicMock()

        with patch.object(
            shell,
            "execute_service_method",
            return_value=None,
        ) as execute_method:
            shell.default("GetDeviceInformation")

        execute_method.assert_called_once_with("GetDeviceInformation", "")

    def test_executes_service_method_with_arguments(self, shell):
        """Verify that a service method with parameters is executed."""
        shell.context.current_service = MagicMock()

        with patch.object(
            shell,
            "execute_service_method",
            return_value=None,
        ) as execute_method:
            shell.default("GetStreamUri ProfileToken=$profile")

        execute_method.assert_called_once_with(
            "GetStreamUri",
            "ProfileToken=$profile",
        )

    def test_suggests_similar_commands(self, shell, capsys):
        """Verify that similar commands are displayed for unknown input."""
        with (
            patch(
                "onvif.cli.interactive.shell.get_device_available_services",
                return_value=[],
            ),
            patch.object(
                shell,
                "get_suggestions",
                return_value=["services", "service"],
            ),
        ):
            shell.default("servce")  # codespell:ignore

        output = capsys.readouterr().out

        assert "Unknown command:" in output
        assert "servce" in output  # codespell:ignore
        assert "Did you mean:" in output
        assert "services" in output

    def test_reports_unknown_command_without_suggestions(self, shell, capsys):
        """Verify that unknown input without suggestions displays help guidance."""
        with (
            patch(
                "onvif.cli.interactive.shell.get_device_available_services",
                return_value=[],
            ),
            patch.object(
                shell,
                "get_suggestions",
                return_value=[],
            ),
        ):
            shell.default("foobar")

        output = capsys.readouterr().out

        assert "Unknown command:" in output
        assert "foobar" in output
        assert "help" in output


class TestInteractiveShellTerminalCommands:
    """Test terminal and shell lifecycle commands."""

    @pytest.fixture
    def shell(self):
        """Create a minimally initialized shell for terminal command tests."""
        shell = object.__new__(InteractiveShell)
        cmd.Cmd.__init__(shell)
        shell.stop_health_check = MagicMock()
        return shell

    def test_emptyline_does_nothing(self, shell):
        """Verify that an empty command does not produce output or an action."""
        assert shell.emptyline() is None

    def test_clear_windows_terminal(self, shell):
        """Verify that Windows terminal clearing emits the Windows escape sequence."""
        with (
            patch("onvif.cli.interactive.shell.sys.platform", "win32"),
            patch("builtins.print") as print_mock,
        ):
            shell.do_clear("")

        print_mock.assert_called_once_with(
            "\033[2J\033[3J\033[H",
            end="",
        )

    def test_clear_posix_terminal(self, shell):
        """Verify that POSIX terminal clearing emits the POSIX escape sequence."""
        with (
            patch("onvif.cli.interactive.shell.sys.platform", "linux"),
            patch("builtins.print") as print_mock,
        ):
            shell.do_clear("")

        print_mock.assert_called_once_with(
            "\033[2J\033[H",
            end="",
        )

    def test_exit_stops_health_check(self, shell):
        """Verify that exiting the shell stops the background health check."""
        result = shell.do_exit("")

        shell.stop_health_check.set.assert_called_once_with()
        assert result is True

    def test_run_starts_command_loop(self, shell):
        """Verify that ``run`` delegates execution to ``cmdloop``."""
        with patch.object(shell, "cmdloop") as cmdloop:
            shell.run()

        cmdloop.assert_called_once_with()

    def test_run_handles_keyboard_interrupt(self, shell):
        """Verify that ``run`` stops the health check and exits on Ctrl-C."""
        with (
            patch.object(
                shell,
                "cmdloop",
                side_effect=KeyboardInterrupt,
            ),
            patch("onvif.cli.interactive.shell.sys.exit") as exit_mock,
        ):
            shell.run()

        shell.stop_health_check.set.assert_called_once_with()
        exit_mock.assert_called_once_with(0)
