"""Tests for CLI discovery helpers."""

from unittest.mock import patch

import pytest

from onvif.cli.helpers.discovery import (
    _print_optional_field,
    _process_device_selection,
    discover_devices,
    select_device_interactive,
)


class TestDiscoverDevices:
    """Tests for discovering ONVIF devices."""

    def test_discovers_devices_with_defaults(self):
        """Test device discovery using the default options."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
            }
        ]

        with (
            patch("onvif.cli.helpers.discovery.ONVIFDiscovery") as mock_discovery,
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            mock_instance = mock_discovery.return_value
            mock_instance.get_local_ip.return_value = "192.168.1.10"
            mock_instance.discover.return_value = devices

            result = discover_devices()

        mock_discovery.assert_called_once_with(
            timeout=4,
            interface=None,
        )
        mock_instance.get_local_ip.assert_called_once_with()
        mock_instance.discover.assert_called_once_with(
            prefer_https=False,
            search=None,
        )
        assert result == devices

    def test_passes_discovery_options(self):
        """Test that discovery options are passed to ONVIFDiscovery."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 443,
                "use_https": True,
            }
        ]

        with (
            patch("onvif.cli.helpers.discovery.ONVIFDiscovery") as mock_discovery,
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            mock_instance = mock_discovery.return_value
            mock_instance.get_local_ip.return_value = "192.168.1.10"
            mock_instance.discover.return_value = devices

            result = discover_devices(
                timeout=10,
                interface="192.168.1.10",
                prefer_https=True,
                filter_term="Hikvision",
            )

        mock_discovery.assert_called_once_with(
            timeout=10,
            interface="192.168.1.10",
        )
        mock_instance.discover.assert_called_once_with(
            prefer_https=True,
            search="Hikvision",
        )
        assert result == devices

    def test_returns_empty_result(self):
        """Test that an empty discovery result is returned unchanged."""
        with (
            patch("onvif.cli.helpers.discovery.ONVIFDiscovery") as mock_discovery,
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            mock_instance = mock_discovery.return_value
            mock_instance.get_local_ip.return_value = "192.168.1.10"
            mock_instance.discover.return_value = []

            result = discover_devices()

        assert result == []


class TestSelectDeviceInteractive:
    """Tests for interactive ONVIF device selection."""

    def test_no_devices(self, capsys):
        """Test that selection is cancelled when no devices are available."""
        result = select_device_interactive([])

        assert result is None
        assert "No ONVIF devices found." in capsys.readouterr().out

    def test_selects_http_device(self):
        """Test selecting an HTTP device."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
                "epr": "uuid:1234",
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="1",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = select_device_interactive(devices)

        assert result == ("192.168.1.17", 80, False)

    def test_selects_https_device(self):
        """Test selecting an HTTPS device."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 443,
                "use_https": True,
                "epr": "urn:uuid:1234",
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="1",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = select_device_interactive(devices)

        assert result == ("192.168.1.17", 443, True)

    @pytest.mark.parametrize(
        "epr",
        [
            "uuid:1234",
            "urn:uuid:1234",
            "1234",
        ],
    )
    def test_displays_device_epr(self, epr, capsys):
        """Test displaying device EPR values with supported prefixes."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
                "epr": epr,
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="q",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = select_device_interactive(devices)

        assert result is None
        assert "1234" in capsys.readouterr().out

    def test_displays_optional_fields(self, capsys):
        """Test displaying available optional device information."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
                "epr": "uuid:1234",
                "hostname": "camera.local",
                "xaddrs": [
                    "http://192.168.1.17/onvif/device_service",
                ],
                "types": [
                    "NetworkVideoTransmitter",
                ],
                "services": [
                    "device",
                    "media",
                ],
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="q",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            select_device_interactive(devices)

        output = capsys.readouterr().out

        assert "camera.local" in output
        assert "http://192.168.1.17/onvif/device_service" in output
        assert "NetworkVideoTransmitter" in output
        assert "device" in output
        assert "media" in output

    def test_displays_date_time(self, capsys):
        """Test displaying UTC and local device date and time."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
                "epr": "uuid:1234",
                "date_time": {
                    "utc": "2026-10-03T12:30:45",
                    "local": "2026-10-03T19:30:45",
                },
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="q",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            select_device_interactive(devices)

        output = capsys.readouterr().out

        assert "12:30:45 03-10-2026" in output
        assert "19:30:45 03-10-2026" in output

    def test_displays_scopes(self, capsys):
        """Test displaying simplified ONVIF scopes and other scopes."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
                "epr": "uuid:1234",
                "scopes": [
                    "onvif://www.onvif.org/name/TestCamera",
                    "onvif://www.onvif.org/hardware/Camera",
                    "http:123",
                ],
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="q",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            select_device_interactive(devices)

        output = capsys.readouterr().out

        assert "[name/TestCamera]" in output
        assert "[hardware/Camera]" in output
        assert "[http:123]" in output

    def test_handles_missing_optional_fields(self, capsys):
        """Test that missing optional fields do not prevent selection."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "epr": "uuid:1234",
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="q",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = select_device_interactive(devices)

        assert result is None
        assert "192.168.1.17:80" in capsys.readouterr().out

    def test_cancels_selection(self):
        """Test cancelling device selection with q."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "epr": "uuid:1234",
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="q",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = select_device_interactive(devices)

        assert result is None


class TestPrintOptionalField:
    """Tests for printing optional device fields."""

    def test_skips_empty_value(self, capsys):
        """Test that empty values are not printed."""
        _print_optional_field("hostname", None)

        assert capsys.readouterr().out == ""

    @pytest.mark.parametrize(
        "value",
        [
            "",
            [],
            {},
            False,
        ],
    )
    def test_skips_falsy_value(self, value, capsys):
        """Test that other falsy values are not printed."""
        _print_optional_field("field", value)

        assert capsys.readouterr().out == ""

    def test_prints_value(self, capsys):
        """Test printing a field value."""
        _print_optional_field("hostname", "camera.local")

        assert "[hostname] camera.local" in capsys.readouterr().out

    def test_colorizes_value(self, capsys):
        """Test colorizing a field value before printing it."""
        with patch(
            "onvif.cli.helpers.discovery.colorize",
            return_value="<colored>",
        ) as mock_colorize:
            _print_optional_field(
                "hostname",
                "camera.local",
                "cyan",
            )

        mock_colorize.assert_called_once_with(
            "camera.local",
            "cyan",
        )
        assert "[hostname] <colored>" in capsys.readouterr().out

    def test_converts_value_to_string(self, capsys):
        """Test that non-string values are converted to text."""
        _print_optional_field("port", 8080)

        assert "[port] 8080" in capsys.readouterr().out


class TestProcessDeviceSelection:
    """Tests for processing interactive device selection."""

    def test_selects_device(self):
        """Test selecting a valid device number."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
            },
            {
                "host": "192.168.1.18",
                "port": 443,
                "use_https": True,
            },
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="2",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = _process_device_selection(
                "http",
                devices,
            )

        assert result == ("192.168.1.18", 443, True)

    def test_selects_http_device(self):
        """Test selecting an HTTP device."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="1",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = _process_device_selection(
                "http",
                devices,
            )

        assert result == ("192.168.1.17", 80, False)

    def test_quits_with_q(self):
        """Test cancelling selection with q."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                return_value="q",
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = _process_device_selection(
                "http",
                devices,
            )

        assert result is None

    def test_retries_invalid_number(self, capsys):
        """Test retrying after an out-of-range device number."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                side_effect=["2", "1"],
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = _process_device_selection(
                "http",
                devices,
            )

        assert result == ("192.168.1.17", 80, False)
        assert "Invalid selection" in capsys.readouterr().out

    def test_retries_invalid_input(self, capsys):
        """Test retrying after non-numeric input."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                side_effect=["abc", "1"],
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = _process_device_selection(
                "http",
                devices,
            )

        assert result == ("192.168.1.17", 80, False)
        assert "Invalid input" in capsys.readouterr().out

    @pytest.mark.parametrize(
        "exception",
        [
            EOFError(),
            KeyboardInterrupt(),
        ],
    )
    def test_handles_input_cancellation(self, exception):
        """Test cancelling selection when terminal input is interrupted."""
        devices = [
            {
                "host": "192.168.1.17",
                "port": 80,
                "use_https": False,
            }
        ]

        with (
            patch(
                "onvif.cli.helpers.discovery.input",
                side_effect=exception,
            ),
            patch(
                "onvif.cli.helpers.discovery.colorize",
                side_effect=lambda value, _color: value,
            ),
        ):
            result = _process_device_selection(
                "http",
                devices,
            )

        assert result is None
