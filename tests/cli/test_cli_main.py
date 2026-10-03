"""Tests for the ONVIF CLI main module."""

from argparse import ArgumentParser
from unittest.mock import Mock, patch

import pytest

from onvif.cli.main import (
    _create_parser,
    _handle_authentication,
    _handle_discovery_mode,
    _process_onvif_client,
    main,
)
from onvif.operator import CacheMode
from onvif.utils import ONVIFOperationException


class TestCreateParser:
    """Tests for creating and configuring the CLI argument parser."""

    def test_creates_parser(self):
        """Test that the CLI argument parser is created correctly."""
        parser = _create_parser()

        assert isinstance(parser, ArgumentParser)
        assert parser.prog == "onvif"

    def test_defaults(self):
        """Test default CLI argument values."""
        parser = _create_parser()

        args = parser.parse_args(
            [
                "--host",
                "192.168.1.17",
                "devicemgmt",
                "GetDeviceInformation",
            ]
        )

        assert args.host == "192.168.1.17"
        assert args.port == 80
        assert args.timeout == 10
        assert args.cache == CacheMode.DB.value
        assert args.discovery_timeout == 4
        assert args.page == 1
        assert args.per_page == 20
        assert args.digest is False
        assert args.https is False
        assert args.no_verify is False
        assert args.no_patch is False
        assert args.interactive is False
        assert args.debug is False

    @pytest.mark.parametrize(
        ("arguments", "attribute", "expected"),
        [
            (["--discover"], "discover", True),
            (["--digest"], "digest", True),
            (["--https"], "https", True),
            (["--no-verify"], "no_verify", True),
            (["--no-patch"], "no_patch", True),
            (["--interactive"], "interactive", True),
            (["--debug"], "debug", True),
            (["--version"], "version", True),
        ],
    )
    def test_boolean_options(self, arguments, attribute, expected):
        """Test boolean CLI options."""
        parser = _create_parser()

        args = parser.parse_args(arguments)

        assert getattr(args, attribute) is expected


class TestHandleDiscoveryMode:
    """Tests for handling CLI device discovery mode."""

    def test_skips_when_disabled(self):
        """Test that discovery mode does nothing when --discover is not set."""
        parser = Mock()
        args = Mock(discover=False)

        with patch("onvif.cli.main.discover_devices") as mock_discover:
            _handle_discovery_mode(parser, args)

        mock_discover.assert_not_called()

    def test_rejects_host(self):
        """Test that discovery cannot be combined with --host."""
        parser = Mock()
        parser.error.side_effect = SystemExit(2)

        args = Mock(
            discover=True,
            host="192.168.1.17",
        )

        with pytest.raises(SystemExit) as exc_info:
            _handle_discovery_mode(parser, args)

        assert exc_info.value.code == 2
        parser.error.assert_called_once()

    def test_no_devices(self):
        """Test discovery failure when no devices are found."""
        parser = Mock()
        args = Mock(
            discover=True,
            host=None,
            filter=None,
            interface=None,
            https=False,
            discovery_timeout=4,
        )

        with patch(
            "onvif.cli.main.discover_devices",
            return_value=[],
        ):
            with pytest.raises(SystemExit) as exc_info:
                _handle_discovery_mode(parser, args)

        assert exc_info.value.code == 1

    def test_no_devices_with_filter(self, capsys):
        """Test discovery failure when a device filter matches no devices."""
        parser = Mock()
        args = Mock(
            discover=True,
            host=None,
            filter="Hikvision",
            interface=None,
            https=False,
            discovery_timeout=4,
        )

        with patch(
            "onvif.cli.main.discover_devices",
            return_value=[],
        ):
            with pytest.raises(SystemExit) as exc_info:
                _handle_discovery_mode(parser, args)

        assert exc_info.value.code == 1
        assert "Hikvision" in capsys.readouterr().out

    def test_selection_cancelled(self):
        """Test discovery when interactive device selection is cancelled."""
        parser = Mock()
        args = Mock(
            discover=True,
            host=None,
            filter=None,
            interface=None,
            https=False,
            discovery_timeout=4,
        )

        devices = [
            ("192.168.1.17", 80, False),
        ]

        with (
            patch(
                "onvif.cli.main.discover_devices",
                return_value=devices,
            ),
            patch(
                "onvif.cli.main.select_device_interactive",
                return_value=None,
            ),
        ):
            with pytest.raises(SystemExit) as exc_info:
                _handle_discovery_mode(parser, args)

        assert exc_info.value.code == 0

    def test_selects_device(self):
        """Test that selected discovery data is applied to CLI arguments."""
        parser = Mock()
        args = Mock(
            discover=True,
            host=None,
            filter="Hikvision",
            interface="192.168.1.1",
            https=True,
            discovery_timeout=10,
        )

        devices = [
            ("192.168.1.17", 443, True),
        ]

        with (
            patch(
                "onvif.cli.main.discover_devices",
                return_value=devices,
            ) as mock_discover,
            patch(
                "onvif.cli.main.select_device_interactive",
                return_value=devices[0],
            ) as mock_select,
        ):
            _handle_discovery_mode(parser, args)

        mock_discover.assert_called_once_with(
            timeout=10,
            interface="192.168.1.1",
            prefer_https=True,
            filter_term="Hikvision",
        )
        mock_select.assert_called_once_with(devices)

        assert args.host == "192.168.1.17"
        assert args.port == 443


class TestHandleAuthentication:
    """Tests for handling CLI authentication credentials."""

    def test_with_credentials(self):
        """Test authentication when credentials are already provided."""
        args = Mock(
            search=None,
            username="admin",
            password="password",
        )

        with (
            patch("builtins.input") as mock_input,
            patch("onvif.cli.main.getpass.getpass") as mock_getpass,
        ):
            _handle_authentication(args)

        mock_input.assert_not_called()
        mock_getpass.assert_not_called()

    def test_prompts_for_credentials(self):
        """Test authentication prompts for missing credentials."""
        args = Mock(
            search=None,
            username=None,
            password=None,
            host="192.168.1.17",
        )

        with (
            patch(
                "builtins.input",
                return_value="admin",
            ) as mock_input,
            patch(
                "onvif.cli.main.getpass.getpass",
                return_value="password",
            ) as mock_getpass,
        ):
            _handle_authentication(args)

        assert args.username == "admin"
        assert args.password == "password"

        mock_input.assert_called_once_with("Enter username: ")
        mock_getpass.assert_called_once()

    @pytest.mark.parametrize(
        "exception",
        [EOFError(), KeyboardInterrupt()],
    )
    def test_username_cancelled(self, exception):
        """Test cancellation of the username prompt."""
        args = Mock(
            search=None,
            username=None,
            password=None,
        )

        with patch(
            "builtins.input",
            side_effect=exception,
        ):
            with pytest.raises(SystemExit) as exc_info:
                _handle_authentication(args)

        assert exc_info.value.code == 1

    @pytest.mark.parametrize(
        "exception",
        [EOFError(), KeyboardInterrupt()],
    )
    def test_password_cancelled(self, exception):
        """Test cancellation of the password prompt."""
        args = Mock(
            search=None,
            username="admin",
            password=None,
            host="192.168.1.17",
        )

        with patch(
            "onvif.cli.main.getpass.getpass",
            side_effect=exception,
        ):
            with pytest.raises(SystemExit) as exc_info:
                _handle_authentication(args)

        assert exc_info.value.code == 1

    def test_skips_credentials_for_search(self):
        """Test that search mode does not request credentials."""
        args = Mock(
            search="hikvision",
            username=None,
            password=None,
        )

        with (
            patch("builtins.input") as mock_input,
            patch("onvif.cli.main.getpass.getpass") as mock_getpass,
        ):
            _handle_authentication(args)

        mock_input.assert_not_called()
        mock_getpass.assert_not_called()


class TestProcessOnvifClient:
    """Tests for creating and processing an ONVIF client."""

    def test_skips_search(self):
        """Test that search mode does not create an ONVIF client."""
        args = Mock(search="hikvision")

        with patch("onvif.cli.main.ONVIFClient") as mock_client:
            _process_onvif_client(args)

        mock_client.assert_not_called()

    def test_direct_command(self):
        """Test direct ONVIF command execution."""
        args = Mock(
            search=None,
            debug=False,
            output=None,
            host="192.168.1.17",
            port=80,
            username="admin",
            password="password",
            digest=False,
            timeout=10,
            cache=CacheMode.DB.value,
            https=False,
            no_verify=False,
            no_patch=False,
            wsdl=None,
            interactive=False,
            service="devicemgmt",
            method="GetDeviceInformation",
            params=["foo", "bar"],
        )

        client = Mock()

        with (
            patch(
                "onvif.cli.main.ONVIFClient",
                return_value=client,
            ) as mock_client,
            patch(
                "onvif.cli.main.execute_command",
                return_value={"result": "ok"},
            ) as mock_execute,
        ):
            _process_onvif_client(args)

        mock_client.assert_called_once_with(
            host="192.168.1.17",
            port=80,
            username="admin",
            password="password",
            http_digest=False,
            timeout=10,
            cache=CacheMode.DB,
            use_https=False,
            verify_ssl=True,
            apply_patch=True,
            capture_xml=False,
            wsdl_dir=None,
        )

        mock_execute.assert_called_once_with(
            client,
            "devicemgmt",
            "GetDeviceInformation",
            "foo bar",
        )

    def test_xml_output_enables_debug(self):
        """Test that XML output automatically enables XML capture."""
        args = Mock(
            search=None,
            debug=False,
            output="result.xml",
            host="192.168.1.17",
            port=80,
            username="admin",
            password="password",
            digest=False,
            timeout=10,
            cache=CacheMode.DB.value,
            https=False,
            no_verify=False,
            no_patch=False,
            wsdl=None,
            interactive=False,
            service="devicemgmt",
            method="GetDeviceInformation",
            params=[],
        )

        client = Mock()

        with (
            patch(
                "onvif.cli.main.ONVIFClient",
                return_value=client,
            ) as mock_client,
            patch(
                "onvif.cli.main.execute_command",
                return_value="<xml/>",
            ),
            patch("onvif.cli.main.save_output_to_file") as mock_save,
        ):
            _process_onvif_client(args)

        assert mock_client.call_args.kwargs["capture_xml"] is True

        mock_save.assert_called_once_with(
            "<xml/>",
            "result.xml",
            True,
            client,
        )

    def test_interactive(self):
        """Test interactive mode."""
        args = Mock(
            search=None,
            debug=False,
            output=None,
            host="192.168.1.17",
            port=80,
            username="admin",
            password="password",
            digest=False,
            timeout=10,
            cache=CacheMode.DB.value,
            https=False,
            no_verify=False,
            no_patch=False,
            wsdl=None,
            interactive=True,
        )

        client = Mock()

        with (
            patch(
                "onvif.cli.main.ONVIFClient",
                return_value=client,
            ),
            patch(
                "onvif.cli.main.InteractiveShell",
            ) as mock_shell,
        ):
            _process_onvif_client(args)

        client.devicemgmt().GetDeviceInformation.assert_called_once()
        mock_shell.assert_called_once_with(client, args)
        mock_shell.return_value.run.assert_called_once()

    def test_connection_error(self):
        """Test interactive mode when the ONVIF connection fails."""
        args = Mock(
            search=None,
            debug=False,
            output=None,
            host="192.168.1.17",
            port=80,
            username="admin",
            password="password",
            digest=False,
            timeout=10,
            cache=CacheMode.DB.value,
            https=False,
            no_verify=False,
            no_patch=False,
            wsdl=None,
            interactive=True,
        )

        client = Mock()
        client.devicemgmt().GetDeviceInformation.side_effect = ONVIFOperationException(
            "Connection failed",
            Exception("Connection failed"),
        )

        with (
            patch(
                "onvif.cli.main.ONVIFClient",
                return_value=client,
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            _process_onvif_client(args)

        assert exc_info.value.code == 1

    def test_keyboard_interrupt(self):
        """Test KeyboardInterrupt handling during command execution."""
        args = Mock(
            search=None,
            debug=False,
            output=None,
            host="192.168.1.17",
            port=80,
            username="admin",
            password="password",
            digest=False,
            timeout=10,
            cache=CacheMode.DB.value,
            use_https=False,
            https=False,
            no_verify=False,
            no_patch=False,
            wsdl=None,
            interactive=False,
            service="devicemgmt",
            method="GetDeviceInformation",
            params=[],
        )

        with (
            patch("onvif.cli.main.ONVIFClient"),
            patch(
                "onvif.cli.main.execute_command",
                side_effect=KeyboardInterrupt,
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            _process_onvif_client(args)

        assert exc_info.value.code == 1

    def test_runtime_error(self):
        """Test RuntimeError handling during command execution."""
        args = Mock(
            search=None,
            debug=False,
            output=None,
            host="192.168.1.17",
            port=80,
            username="admin",
            password="password",
            digest=False,
            timeout=10,
            use_https=False,
            cache=CacheMode.DB.value,
            https=False,
            no_verify=False,
            no_patch=False,
            wsdl=None,
            interactive=False,
            service="devicemgmt",
            method="GetDeviceInformation",
            params=[],
        )

        with (
            patch("onvif.cli.main.ONVIFClient"),
            patch(
                "onvif.cli.main.execute_command",
                side_effect=RuntimeError("Something went wrong"),
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            _process_onvif_client(args)

        assert exc_info.value.code == 1


class TestMain:
    """Tests for the main ONVIF CLI entry point."""

    def test_no_arguments(self, capsys):
        """Test that no arguments prints help and exits successfully."""
        with (
            patch("onvif.cli.main.sys.argv", ["onvif"]),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        assert "usage:" in capsys.readouterr().out.lower()

    def test_version(self, capsys):
        """Test the --version option."""
        with (
            patch(
                "onvif.cli.main.sys.argv",
                ["onvif", "--version"],
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        assert capsys.readouterr().out.strip()

    def test_search(self):
        """Test product search mode."""
        with (
            patch(
                "onvif.cli.main.sys.argv",
                ["onvif", "--search", "hikvision"],
            ),
            patch("onvif.cli.main.search_products") as mock_search,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 0
        mock_search.assert_called_once_with("hikvision", 1, 20)

    def test_requires_service_and_method(self):
        """Test validation when service and method are missing."""
        with (
            patch(
                "onvif.cli.main.sys.argv",
                ["onvif", "--host", "192.168.1.17"],
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 2

    def test_requires_host(self):
        """Test validation when the host is missing."""
        with (
            patch(
                "onvif.cli.main.sys.argv",
                [
                    "onvif",
                    "devicemgmt",
                    "GetDeviceInformation",
                ],
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 2

    def test_calls_handlers(self):
        """Test that the main execution flow calls the expected handlers."""
        with (
            patch(
                "onvif.cli.main.sys.argv",
                [
                    "onvif",
                    "--host",
                    "192.168.1.17",
                    "--username",
                    "admin",
                    "--password",
                    "password",
                    "devicemgmt",
                    "GetDeviceInformation",
                ],
            ),
            patch(
                "onvif.cli.main._handle_discovery_mode",
            ) as mock_discovery,
            patch(
                "onvif.cli.main._handle_authentication",
            ) as mock_auth,
            patch(
                "onvif.cli.main._process_onvif_client",
            ) as mock_process,
        ):
            main()

        mock_discovery.assert_called_once()
        mock_auth.assert_called_once()
        mock_process.assert_called_once()

    def test_rejects_output_with_interactive(self):
        """Test that --output cannot be combined with --interactive."""
        with (
            patch(
                "onvif.cli.main.sys.argv",
                [
                    "onvif",
                    "--host",
                    "192.168.1.17",
                    "--interactive",
                    "--output",
                    "result.json",
                ],
            ),
            pytest.raises(SystemExit) as exc_info,
        ):
            main()

        assert exc_info.value.code == 2
