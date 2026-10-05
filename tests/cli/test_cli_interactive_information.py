"""Tests for ONVIF interactive shell information commands."""

from datetime import datetime
from unittest.mock import MagicMock, patch

from requests.exceptions import RequestException
from zeep.exceptions import TransportError

from onvif.cli.interactive.information import InformationCommands
from onvif.utils.exceptions import ONVIFOperationException


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
    """Create a mocked shell context."""
    context = MagicMock()

    context.args = create_args(**overrides)
    context.client = overrides.get("client", MagicMock())
    context.device_info_text = overrides.get(
        "device_info_text",
        "\n\n[Device Info]\n  Manufacturer  : Test Manufacturer",
    )

    context.stored_data = {}
    context.stored_metadata = {}

    context.last_result = overrides.get("last_result", None)
    context.last_method = overrides.get("last_method", None)
    context.last_service_name = overrides.get("last_service_name", None)
    context.last_operation_timestamp = overrides.get("last_operation_timestamp", None)

    return context


def create_commands(**overrides):
    """Create InformationCommands with a mocked shell context."""
    commands = InformationCommands()
    commands.context = create_context(**overrides)
    commands._handle_connection_error = MagicMock()  # pylint: disable=protected-access
    return commands


class TestInformationCommandsHelp:
    """Test help and shortcut commands."""

    def test_do_help_without_argument(self, capsys):
        """Verify help displays interactive help when no argument is provided."""
        commands = create_commands()

        with patch(
            "onvif.cli.interactive.information.INTERACTIVE_HELP",
            "interactive help text",
        ):
            commands.do_help("")

        captured = capsys.readouterr()
        assert captured.out == "interactive help text\n"

    def test_do_help_with_argument(self):
        """Verify help delegates to cmd.Cmd for a specific topic."""
        commands = create_commands()

        with patch("onvif.cli.interactive.information.cmd.Cmd.do_help") as do_help:
            commands.do_help("capabilities")

        do_help.assert_called_once_with(commands, "capabilities")

    def test_do_shortcuts(self, capsys):
        """Verify shortcuts displays the interactive shortcuts."""
        commands = create_commands()

        with patch(
            "onvif.cli.interactive.information.INTERACTIVE_SHORTCUTS",
            "shortcut text",
        ):
            commands.do_shortcuts("")

        captured = capsys.readouterr()
        assert captured.out == "shortcut text\n"


class TestInformationCommandsInfo:
    """Test connection and device information output."""

    def test_do_info_displays_basic_connection_information(self, capsys):
        """Verify basic connection information is displayed."""
        commands = create_commands(
            host="10.0.0.10",
            port=8080,
            digest=True,
            device_info_text="DEVICE INFO",
        )

        commands.do_info("")

        output = capsys.readouterr().out

        assert "10.0.0.10:8080" in output
        assert "HTTP Digest" in output
        assert "DEVICE INFO" in output

    def test_do_info_displays_ws_username_token_when_digest_disabled(self, capsys):
        """Verify WS-UsernameToken is displayed when digest authentication is disabled."""
        commands = create_commands(digest=False)

        commands.do_info("")

        output = capsys.readouterr().out

        assert "WS-UsernameToken" in output
        assert "HTTP Digest" not in output

    def test_do_info_displays_https(self, capsys):
        """Verify HTTPS status is displayed when enabled."""
        commands = create_commands(https=True)

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Use HTTPS" in output
        assert "True" in output

    def test_do_info_hides_https_when_disabled(self, capsys):
        """Verify HTTPS status is omitted when disabled."""
        commands = create_commands(https=False)

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Use HTTPS" not in output

    def test_do_info_displays_ssl_verification_disabled(self, capsys):
        """Verify disabled SSL verification is displayed."""
        commands = create_commands(no_verify_ssl=True)

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Verify SSL" in output
        assert "False" in output

    def test_do_info_displays_non_default_timeout(self, capsys):
        """Verify a non-default timeout is displayed."""
        commands = create_commands(timeout=30)

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Timeout" in output
        assert "30s" in output

    def test_do_info_hides_default_timeout(self, capsys):
        """Verify the default timeout is omitted."""
        commands = create_commands(timeout=10)

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Timeout" not in output

    def test_do_info_displays_debug_mode(self, capsys):
        """Verify debug mode is displayed when enabled."""
        commands = create_commands(debug=True)

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Debug Mode" in output
        assert "True" in output

    def test_do_info_displays_no_patch(self, capsys):
        """Verify disabled ZeepPatcher status is displayed."""
        commands = create_commands(no_patch=True)

        commands.do_info("")

        output = capsys.readouterr().out

        assert "ZeepPatcher" in output
        assert "Disabled" in output

    def test_do_info_displays_custom_wsdl(self, capsys):
        """Verify custom WSDL path is displayed."""
        commands = create_commands(wsdl="/custom/wsdl")

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Custom WSDL" in output
        assert "/custom/wsdl" in output

    def test_do_info_displays_non_default_health_check_interval(self, capsys):
        """Verify a non-default health check interval is displayed."""
        commands = create_commands(health_check_interval=30)

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Health Check" in output
        assert "30s" in output

    def test_do_info_hides_default_health_check_interval(self, capsys):
        """Verify the default health check interval is omitted."""
        commands = create_commands(health_check_interval=10)

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Health Check" not in output

    def test_do_info_displays_multiple_options(self, capsys):
        """Verify multiple enabled options are displayed together."""
        commands = create_commands(
            https=True,
            no_verify_ssl=True,
            timeout=30,
            debug=True,
            no_patch=True,
            wsdl="/custom/wsdl",
            health_check_interval=20,
        )

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Use HTTPS" in output
        assert "Verify SSL" in output
        assert "Timeout" in output
        assert "Debug Mode" in output
        assert "ZeepPatcher" in output
        assert "Custom WSDL" in output
        assert "Health Check" in output

    def test_do_info_displays_device_information(self, capsys):
        """Verify stored device information is included."""
        commands = create_commands(
            device_info_text="Manufacturer: Test Camera\nModel: Test Model"
        )

        commands.do_info("")

        output = capsys.readouterr().out

        assert "Manufacturer: Test Camera" in output
        assert "Model: Test Model" in output


class TestInformationCommandsCapabilities:
    """Test device capabilities commands."""

    def test_do_capabilities_uses_cached_capabilities(self, capsys):
        """Verify cached capabilities are used when available."""
        capabilities = {"Device": {"System": {"DiscoveryResolve": True}}}

        client = MagicMock()
        client.capabilities = capabilities

        commands = create_commands(client=client)

        with patch(
            "onvif.cli.interactive.information.format_capabilities_as_services",
            return_value="formatted capabilities",
        ) as formatter:
            commands.do_capabilities("")

        client.devicemgmt.assert_not_called()
        formatter.assert_called_once_with(capabilities)

        captured = capsys.readouterr()
        assert captured.out == "formatted capabilities\n"

    def test_do_capabilities_fetches_capabilities_when_not_cached(self, capsys):
        """Verify capabilities are fetched when no cached value exists."""
        capabilities = {"Device": {"System": {}}}

        client = MagicMock()
        client.capabilities = None
        client.devicemgmt().GetCapabilities.return_value = capabilities

        commands = create_commands(client=client)

        with patch(
            "onvif.cli.interactive.information.format_capabilities_as_services",
            return_value="formatted capabilities",
        ) as formatter:
            commands.do_capabilities("")

        client.devicemgmt().GetCapabilities.assert_called_once_with(Category="All")
        formatter.assert_called_once_with(capabilities)

        captured = capsys.readouterr()
        assert captured.out == "formatted capabilities\n"

    def test_do_capabilities_stores_result(self):
        """Verify capabilities are stored in the shell context."""
        capabilities = {"Device": {"System": {}}}

        client = MagicMock()
        client.capabilities = capabilities

        commands = create_commands(client=client)

        with patch(
            "onvif.cli.interactive.information.format_capabilities_as_services",
            return_value="formatted",
        ):
            commands.do_capabilities("")

        assert commands.context.stored_data["capabilities"] == capabilities
        assert commands.context.stored_metadata["capabilities"] == {
            "service": "devicemgmt",
            "method": "GetCapabilities",
        }

    def test_do_capabilities_handles_connection_error(self):
        """Verify connection errors trigger the connection error handler."""
        exception = ONVIFOperationException(
            "GetCapabilities",
            RequestException("connection failed"),
        )

        client = MagicMock()
        client.capabilities = None
        client.devicemgmt().GetCapabilities.side_effect = exception

        commands = create_commands(client=client)

        commands.do_capabilities("")

        commands._handle_connection_error.assert_called_once_with()  # pylint: disable=protected-access

    def test_do_capabilities_prints_non_connection_error(self, capsys):
        """Verify non-connection operation errors are printed."""
        exception = ONVIFOperationException(
            "GetCapabilities",
            ValueError("invalid response"),
        )

        client = MagicMock()
        client.capabilities = None
        client.devicemgmt().GetCapabilities.side_effect = exception

        commands = create_commands(client=client)

        commands.do_capabilities("")

        captured = capsys.readouterr()

        assert "Error:" in captured.out
        assert "invalid response" in captured.out
        commands._handle_connection_error.assert_not_called()  # pylint: disable=protected-access

    def test_do_caps_delegates_to_capabilities(self):
        """Verify caps is an alias for capabilities."""
        commands = create_commands()

        with patch.object(commands, "do_capabilities") as do_capabilities:
            commands.do_caps("test")

        do_capabilities.assert_called_once_with("test")


class TestInformationCommandsServices:
    """Test device services commands."""

    def test_do_services_uses_cached_services(self, capsys):
        """Verify cached services are used when available."""
        services = ["devicemgmt", "media"]

        client = MagicMock()
        client.services = services

        commands = create_commands(client=client)

        with patch(
            "onvif.cli.interactive.information.format_services_list",
            return_value="formatted services",
        ) as formatter:
            commands.do_services("")

        client.devicemgmt.assert_not_called()
        formatter.assert_called_once_with(services)

        captured = capsys.readouterr()
        assert captured.out == "formatted services\n"

    def test_do_services_fetches_services_when_not_cached(self, capsys):
        """Verify services are fetched when no cached value exists."""
        services = ["devicemgmt", "media"]

        client = MagicMock()
        client.services = None
        client.devicemgmt().GetServices.return_value = services

        commands = create_commands(client=client)

        with patch(
            "onvif.cli.interactive.information.format_services_list",
            return_value="formatted services",
        ) as formatter:
            commands.do_services("")

        client.devicemgmt().GetServices.assert_called_once_with(IncludeCapability=False)
        formatter.assert_called_once_with(services)

        captured = capsys.readouterr()
        assert captured.out == "formatted services\n"

    def test_do_services_stores_result(self):
        """Verify services are stored in the shell context."""
        services = ["devicemgmt", "media"]

        client = MagicMock()
        client.services = services

        commands = create_commands(client=client)

        with patch(
            "onvif.cli.interactive.information.format_services_list",
            return_value="formatted",
        ):
            commands.do_services("")

        assert commands.context.stored_data["services"] == services
        assert commands.context.stored_metadata["services"] == {
            "service": "devicemgmt",
            "method": "GetServices",
        }

    def test_do_services_handles_connection_error(self):
        """Verify connection errors trigger the connection error handler."""
        exception = ONVIFOperationException(
            "GetServices",
            TransportError("connection failed"),
        )

        client = MagicMock()
        client.services = None
        client.devicemgmt().GetServices.side_effect = exception

        commands = create_commands(client=client)

        commands.do_services("")

        commands._handle_connection_error.assert_called_once_with()  # pylint: disable=protected-access

    def test_do_services_prints_non_connection_error(self, capsys):
        """Verify non-connection operation errors are printed."""
        exception = ONVIFOperationException(
            "GetServices",
            ValueError("invalid response"),
        )

        client = MagicMock()
        client.services = None
        client.devicemgmt().GetServices.side_effect = exception

        commands = create_commands(client=client)

        commands.do_services("")

        captured = capsys.readouterr()

        assert "Error:" in captured.out
        assert "invalid response" in captured.out
        commands._handle_connection_error.assert_not_called()  # pylint: disable=protected-access


class TestInformationCommandsDebug:
    """Test debug information command."""

    def test_do_debug_displays_xml_information(self, capsys):
        """Verify debug output includes captured SOAP XML."""
        client = MagicMock()
        client.xml_plugin = MagicMock()
        client.xml_plugin.last_sent_xml = "<request>test</request>"
        client.xml_plugin.last_received_xml = "<response>test</response>"

        commands = create_commands(client=client)

        commands.do_debug("")

        output = capsys.readouterr().out

        assert "Last SOAP Request:" in output
        assert "<request>test</request>" in output
        assert "Last SOAP Response:" in output
        assert "<response>test</response>" in output

    def test_do_debug_displays_none_when_xml_is_missing(self, capsys):
        """Verify missing XML capture is displayed as None."""
        client = MagicMock()
        client.xml_plugin = MagicMock()
        client.xml_plugin.last_sent_xml = None
        client.xml_plugin.last_received_xml = None

        commands = create_commands(client=client)

        commands.do_debug("")

        output = capsys.readouterr().out

        assert "Last SOAP Request:" in output
        assert "Last SOAP Response:" in output
        assert "None" in output

    def test_do_debug_displays_last_operation(self, capsys):
        """Verify the last operation metadata is displayed."""
        client = MagicMock()
        client.xml_plugin = MagicMock()

        timestamp = datetime(2026, 10, 5, 14, 30, 45)

        commands = create_commands(
            client=client,
            last_method="GetDeviceInformation",
            last_service_name="devicemgmt",
            last_operation_timestamp=timestamp,
        )

        commands.do_debug("")

        output = capsys.readouterr().out

        assert "Last Operation:" in output
        assert "operation: devicemgmt.GetDeviceInformation()" in output
        assert "timestamp: 2026-10-05 14:30:45" in output

    def test_do_debug_hides_last_operation_when_no_method(self, capsys):
        """Verify operation metadata is omitted when no method was executed."""
        client = MagicMock()
        client.xml_plugin = MagicMock()

        commands = create_commands(client=client)

        commands.do_debug("")

        output = capsys.readouterr().out

        assert "Last Operation:" not in output
        assert "Last SOAP Request:" in output

    def test_do_debug_hides_last_operation_when_no_timestamp(self, capsys):
        """Verify operation metadata is omitted when no timestamp exists."""
        client = MagicMock()
        client.xml_plugin = MagicMock()

        commands = create_commands(
            client=client,
            last_method="GetDeviceInformation",
            last_service_name="devicemgmt",
            last_operation_timestamp=None,
        )

        commands.do_debug("")

        output = capsys.readouterr().out

        assert "Last Operation:" not in output

    def test_do_debug_handles_disabled_xml_plugin(self, capsys):
        """Verify debug command reports when XML capture is unavailable."""
        client = MagicMock()
        client.xml_plugin = None

        commands = create_commands(client=client)

        commands.do_debug("")

        output = capsys.readouterr().out

        assert "Debug mode not enabled" in output
        assert "--debug" in output
