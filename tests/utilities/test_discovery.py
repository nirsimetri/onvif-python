# pylint: disable=too-many-lines
"""Tests for ONVIFDiscovery."""

import socket
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from onvif.utils.discovery import ONVIFDiscovery
from onvif.utils.exceptions import ONVIFOperationException


@pytest.fixture
def discovery():
    """Fixture that returns an instance of ONVIFDiscovery for testing."""
    return ONVIFDiscovery()


@pytest.fixture
def discovery_with_interface():
    """Fixture that returns an instance of ONVIFDiscovery with a specific interface."""
    return ONVIFDiscovery(timeout=7, interface="192.168.1.10")


# pylint: disable=protected-access
class TestONVIFDiscoveryInitialization:
    """Tests for the initialization of the ONVIFDiscovery class."""

    def test_init_defaults(self):
        """Test that the default values are set correctly."""
        instance = ONVIFDiscovery()

        assert instance.timeout == 4
        assert instance.interface is None
        assert instance._local_ip is None

    def test_init_custom_values(self):
        """Test that custom values are set correctly."""
        instance = ONVIFDiscovery(
            timeout=10,
            interface="192.168.1.20",
        )

        assert instance.timeout == 10
        assert instance.interface == "192.168.1.20"
        assert instance._local_ip is None


class TestGetLocalIP:
    """Tests for the get_local_ip method of ONVIFDiscovery."""

    def test_get_local_ip_returns_cached_value(self, discovery):
        """Test that get_local_ip returns the cached value if already set."""
        discovery._local_ip = "192.168.1.50"

        with patch("onvif.utils.discovery.socket.socket") as mock_socket:
            assert discovery.get_local_ip() == "192.168.1.50"

        mock_socket.assert_not_called()

    def test_get_local_ip_uses_configured_interface(self, discovery_with_interface):
        """Test that get_local_ip uses the configured network interface."""
        assert discovery_with_interface.get_local_ip() == "192.168.1.10"
        assert discovery_with_interface._local_ip == "192.168.1.10"

    def test_get_local_ip_uses_default_route(self, discovery):
        """Test that get_local_ip resolves the address using the default route."""
        sock = Mock()
        sock.getsockname.return_value = ("192.168.1.25", 0)

        with patch(
            "onvif.utils.discovery.socket.socket",
            return_value=sock,
        ) as mock_socket:
            result = discovery.get_local_ip()

        assert result == "192.168.1.25"
        assert discovery._local_ip == "192.168.1.25"

        mock_socket.assert_called_once_with(
            discovery_module_socket_af_inet(),
            discovery_module_socket_dgram(),
        )
        sock.connect.assert_called_once_with(("8.8.8.8", 80))
        sock.getsockname.assert_called_once()
        sock.close.assert_called_once()

    def test_get_local_ip_falls_back_to_hostname(self, discovery):
        """Test that get_local_ip falls back to hostname resolution on failure."""
        sock = Mock()
        sock.connect.side_effect = OSError("network unavailable")

        with (
            patch(
                "onvif.utils.discovery.socket.socket",
                return_value=sock,
            ),
            patch(
                "onvif.utils.discovery.socket.gethostname",
                return_value="camera-host",
            ),
            patch(
                "onvif.utils.discovery.socket.gethostbyname",
                return_value="192.168.1.30",
            ),
        ):
            result = discovery.get_local_ip()

        assert result == "192.168.1.30"
        assert discovery._local_ip == "192.168.1.30"

    def test_get_local_ip_hostname_loopback_falls_back_to_empty_string(self, discovery):
        """Test that hostname resolution falls back to an empty address for loopback."""
        sock = Mock()
        sock.connect.side_effect = OSError("network unavailable")

        with (
            patch(
                "onvif.utils.discovery.socket.socket",
                return_value=sock,
            ),
            patch(
                "onvif.utils.discovery.socket.gethostname",
                return_value="camera-host",
            ),
            patch(
                "onvif.utils.discovery.socket.gethostbyname",
                return_value="127.0.0.1",
            ),
        ):
            result = discovery.get_local_ip()

        assert result == ""
        assert discovery._local_ip == ""

    def test_get_local_ip_hostname_lookup_failure_returns_empty_string(self, discovery):
        """Test that get_local_ip returns an empty string when hostname resolution
        fails."""
        sock = Mock()
        sock.connect.side_effect = OSError("network unavailable")

        with (
            patch(
                "onvif.utils.discovery.socket.socket",
                return_value=sock,
            ),
            patch(
                "onvif.utils.discovery.socket.gethostname",
                return_value="camera-host",
            ),
            patch(
                "onvif.utils.discovery.socket.gethostbyname",
                side_effect=OSError("hostname lookup failed"),
            ),
        ):
            result = discovery.get_local_ip()

        assert result == ""
        assert discovery._local_ip == ""


class TestParseXAddr:
    """Tests for the _parse_xaddr method of ONVIFDiscovery."""

    @pytest.mark.parametrize(
        ("xaddrs", "prefer_https", "expected"),
        [
            (
                ["http://192.168.1.100/onvif/device_service"],
                False,
                {
                    "host": "192.168.1.100",
                    "port": 80,
                    "use_https": False,
                },
            ),
            (
                ["http://192.168.1.100:8080/onvif/device_service"],
                False,
                {
                    "host": "192.168.1.100",
                    "port": 8080,
                    "use_https": False,
                },
            ),
            (
                ["https://192.168.1.100/onvif/device_service"],
                False,
                {
                    "host": "192.168.1.100",
                    "port": 443,
                    "use_https": True,
                },
            ),
            (
                ["https://192.168.1.100:8443/onvif/device_service"],
                False,
                {
                    "host": "192.168.1.100",
                    "port": 8443,
                    "use_https": True,
                },
            ),
            (
                [
                    "http://192.168.1.100/onvif/device_service",
                    "https://192.168.1.100/onvif/device_service",
                ],
                True,
                {
                    "host": "192.168.1.100",
                    "port": 443,
                    "use_https": True,
                },
            ),
        ],
    )
    def test_parse_xaddr(self, discovery, xaddrs, prefer_https, expected):
        """Test that _parse_xaddr extracts the connection details from XAddrs."""
        device_info = {
            "xaddrs": xaddrs,
            "host": None,
            "port": 80,
            "use_https": False,
        }

        discovery._parse_xaddr(device_info, prefer_https)

        assert device_info["host"] == expected["host"]
        assert device_info["port"] == expected["port"]
        assert device_info["use_https"] == expected["use_https"]

    def test_parse_xaddr_prefers_https_when_available(self, discovery):
        """Test that _parse_xaddr selects an HTTPS XAddr when HTTPS is preferred."""
        device_info = {
            "xaddrs": [
                "http://192.168.1.100:80/onvif/device_service",
                "https://192.168.1.100:8443/onvif/device_service",
            ],
            "host": None,
            "port": 80,
            "use_https": False,
        }

        discovery._parse_xaddr(device_info, prefer_https=True)

        assert device_info["host"] == "192.168.1.100"
        assert device_info["port"] == 8443
        assert device_info["use_https"] is True

    def test_parse_xaddr_falls_back_to_first_xaddr_when_https_not_available(
        self,
        discovery,
    ):
        """Test that _parse_xaddr falls back to the first XAddr without HTTPS."""
        device_info = {
            "xaddrs": [
                "http://192.168.1.100:8080/onvif/device_service",
                "http://192.168.1.101:9090/onvif/device_service",
            ],
            "host": None,
            "port": 80,
            "use_https": False,
        }

        discovery._parse_xaddr(device_info, prefer_https=True)

        assert device_info["host"] == "192.168.1.100"
        assert device_info["port"] == 8080
        assert device_info["use_https"] is False

    def test_parse_xaddr_invalid_port_logs_warning(self, discovery, caplog):
        """Test that _parse_xaddr logs a warning when an XAddr has an invalid port."""
        device_info = {
            "xaddrs": ["http://192.168.1.100:invalid/onvif/device_service"],
            "host": None,
            "port": 80,
            "use_https": False,
        }

        with caplog.at_level("WARNING"):
            discovery._parse_xaddr(device_info)

        assert device_info["host"] is None
        assert device_info["port"] == 80
        assert device_info["use_https"] is False
        assert "Error occurred while parsing XAddr" in caplog.text

    def test_parse_xaddr_https_port_implies_https(self, discovery):
        """Test that port 443 causes an XAddr to be treated as HTTPS."""
        device_info = {
            "xaddrs": ["http://192.168.1.100:443/onvif/device_service"],
            "host": None,
            "port": 80,
            "use_https": False,
        }

        discovery._parse_xaddr(device_info)

        assert device_info["host"] == "192.168.1.100"
        assert device_info["port"] == 443
        assert device_info["use_https"] is True

    def test_parse_xaddr_https_default_port(self, discovery):
        """Test that HTTPS XAddrs without an explicit port use port 443."""
        device_info = {
            "xaddrs": ["https://camera.example.com/onvif/device_service"],
            "host": None,
            "port": 80,
            "use_https": False,
        }

        discovery._parse_xaddr(device_info)

        assert device_info["host"] == "camera.example.com"
        assert device_info["port"] == 443
        assert device_info["use_https"] is True


class TestParseSingleResponse:
    """Tests for the _parse_single_response method of ONVIFDiscovery."""

    def test_parse_single_response_valid(self, discovery):
        """Test that _parse_single_response parses a valid WS-Discovery response."""
        xml = """
        <soap:Envelope
            xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
            xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing"
            xmlns:wsd="http://schemas.xmlsoap.org/ws/2005/04/discovery"
            xmlns:tds="http://www.onvif.org/ver10/device/wsdl">
        <soap:Body>
            <wsd:ProbeMatches>
            <wsd:ProbeMatch>
                <wsa:EndpointReference>
                <wsa:Address>urn:uuid:device-123</wsa:Address>
                </wsa:EndpointReference>
                <wsd:Types>tds:Device tds:NetworkVideoTransmitter</wsd:Types>
                <wsd:Scopes>
                onvif://www.onvif.org/type/NetworkVideoTransmitter
                onvif://www.onvif.org/name/TestCamera
                </wsd:Scopes>
                <wsd:XAddrs>
                http://192.168.1.100/onvif/device_service
                </wsd:XAddrs>
            </wsd:ProbeMatch>
            </wsd:ProbeMatches>
        </soap:Body>
        </soap:Envelope>
        """

        result = discovery._parse_single_response(xml)

        assert result == {
            "epr": "urn:uuid:device-123",
            "types": ["tds:Device", "tds:NetworkVideoTransmitter"],
            "scopes": [
                "onvif://www.onvif.org/type/NetworkVideoTransmitter",
                "onvif://www.onvif.org/name/TestCamera",
            ],
            "xaddrs": ["http://192.168.1.100/onvif/device_service"],
            "host": "192.168.1.100",
            "port": 80,
            "use_https": False,
        }

    def test_parse_single_response_without_probe_match_returns_none(self, discovery):
        """Test that _parse_single_response returns None without a ProbeMatch
        element."""
        xml = """
        <soap:Envelope
            xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
        <soap:Body>
            <NotAProbeMatch />
        </soap:Body>
        </soap:Envelope>
        """

        assert discovery._parse_single_response(xml) is None

    def test_parse_single_response_invalid_xml_returns_none(self, discovery):
        """Test that _parse_single_response returns None for malformed XML."""
        assert discovery._parse_single_response("<invalid") is None

    def test_parse_single_response_without_xaddr_returns_default_device_info(
        self,
        discovery,
    ):
        """Test that a ProbeMatch without XAddrs returns default connection
        information."""
        xml = """
        <soap:Envelope
            xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
            xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing"
            xmlns:wsd="http://schemas.xmlsoap.org/ws/2005/04/discovery">
        <soap:Body>
            <wsd:ProbeMatches>
            <wsd:ProbeMatch>
                <wsa:EndpointReference>
                <wsa:Address>urn:uuid:device-123</wsa:Address>
                </wsa:EndpointReference>
            </wsd:ProbeMatch>
            </wsd:ProbeMatches>
        </soap:Body>
        </soap:Envelope>
        """

        result = discovery._parse_single_response(xml)

        assert result == {
            "epr": "urn:uuid:device-123",
            "types": [],
            "scopes": [],
            "xaddrs": [],
            "host": None,
            "port": 80,
            "use_https": False,
        }

    def test_parse_single_response_empty_optional_elements(self, discovery):
        """Test that empty optional ProbeMatch elements produce empty values."""
        xml = """
        <soap:Envelope
            xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
            xmlns:wsd="http://schemas.xmlsoap.org/ws/2005/04/discovery">
        <soap:Body>
            <wsd:ProbeMatches>
            <wsd:ProbeMatch>
                <wsd:Types />
                <wsd:Scopes />
                <wsd:XAddrs />
            </wsd:ProbeMatch>
            </wsd:ProbeMatches>
        </soap:Body>
        </soap:Envelope>
        """

        result = discovery._parse_single_response(xml)

        assert result["epr"] == ""
        assert result["types"] == []
        assert result["scopes"] == []
        assert result["xaddrs"] == []
        assert result["host"] is None


class TestParseResponses:
    """Tests for the _parse_responses method of ONVIFDiscovery."""

    def test_parse_responses_returns_valid_devices(self, discovery):
        """Test that _parse_responses returns successfully parsed devices."""
        device = {
            "host": "192.168.1.100",
            "port": 80,
        }

        with patch.object(
            discovery,
            "_parse_single_response",
            return_value=device,
        ) as parse_response:
            result = discovery._parse_responses(
                [
                    {"xml": "<device />"},
                ]
            )

        assert result == [device]
        parse_response.assert_called_once_with(
            "<device />",
            False,
        )

    def test_parse_responses_skips_device_without_host(self, discovery):
        """Test that _parse_responses skips devices without a host address."""
        with patch.object(
            discovery,
            "_parse_single_response",
            return_value={
                "host": None,
                "port": 80,
            },
        ):
            result = discovery._parse_responses([{"xml": "<device />"}])

        assert result == []

    def test_parse_responses_skips_malformed_response(self, discovery):
        """Test that _parse_responses skips responses that fail during parsing."""
        with patch.object(
            discovery,
            "_parse_single_response",
            side_effect=ValueError("invalid response"),
        ):
            result = discovery._parse_responses([{"xml": "<invalid />"}])

        assert result == []

    def test_parse_responses_handles_missing_xml(self, discovery):
        """Test that _parse_responses ignores responses without XML content."""
        result = discovery._parse_responses([{"address": "192.168.1.100"}])

        assert result == []

    def test_parse_responses_passes_prefer_https(self, discovery):
        """Test that _parse_responses forwards the HTTPS preference to the parser."""
        device = {
            "host": "192.168.1.100",
            "port": 443,
        }

        with patch.object(
            discovery,
            "_parse_single_response",
            return_value=device,
        ) as parse_response:
            result = discovery._parse_responses(
                [{"xml": "<device />"}],
                prefer_https=True,
            )

        assert result == [device]
        parse_response.assert_called_once_with(
            "<device />",
            True,
        )


class TestFilterDevices:
    """Tests for the _filter_devices method of ONVIFDiscovery."""

    def test_filter_devices_empty_search_returns_original_list(self, discovery):
        """Test that an empty search term returns the original device list."""
        devices = [
            {"host": "192.168.1.100", "types": []},
            {"host": "192.168.1.101", "types": []},
        ]

        result = discovery._filter_devices(devices, "")

        assert result is devices

    def test_filter_devices_matches_type_case_insensitively(self, discovery):
        """Test that device filtering matches device types case-insensitively."""
        devices = [
            {
                "host": "192.168.1.100",
                "types": ["tds:NetworkVideoTransmitter"],
                "scopes": [],
            },
            {
                "host": "192.168.1.101",
                "types": ["tds:Device"],
                "scopes": [],
            },
        ]

        result = discovery._filter_devices(
            devices,
            "networkvideotransmitter",
        )

        assert result == [devices[0]]

    def test_filter_devices_matches_scope_case_insensitively(self, discovery):
        """Test that device filtering matches scopes case-insensitively."""
        devices = [
            {
                "host": "192.168.1.100",
                "types": [],
                "scopes": ["onvif://www.onvif.org/name/Hikvision"],
            },
            {
                "host": "192.168.1.101",
                "types": [],
                "scopes": ["onvif://www.onvif.org/name/Dahua"],
            },
        ]

        result = discovery._filter_devices(
            devices,
            "hikvision",
        )

        assert result == [devices[0]]

    def test_filter_devices_matches_type_or_scope(self, discovery):
        """Test that device filtering matches either device types or scopes."""
        devices = [
            {
                "host": "192.168.1.100",
                "types": ["NetworkVideoTransmitter"],
                "scopes": [],
            },
            {
                "host": "192.168.1.101",
                "types": [],
                "scopes": ["Camera"],
            },
            {
                "host": "192.168.1.102",
                "types": ["Device"],
                "scopes": ["Other"],
            },
        ]

        result = discovery._filter_devices(
            devices,
            "camera",
        )

        assert result == [devices[1]]

    def test_filter_devices_handles_missing_types_and_scopes(self, discovery):
        """Test that device filtering handles missing types and scopes gracefully."""
        devices = [
            {"host": "192.168.1.100"},
            {
                "host": "192.168.1.101",
                "types": ["Camera"],
            },
            {
                "host": "192.168.1.102",
                "scopes": ["Camera"],
            },
        ]

        result = discovery._filter_devices(
            devices,
            "camera",
        )

        assert result == [devices[1], devices[2]]


class TestProcessDevice:
    """Tests for the _process_device method of ONVIFDiscovery."""

    def test_process_device_initializes_enrichment_fields(self, discovery):
        """Test that _process_device initializes device enrichment fields."""
        device = {
            "host": "192.168.1.100",
            "port": 80,
        }

        client = Mock()
        client.services = []

        device_service = Mock()
        client.devicemgmt.return_value = device_service

        with (
            patch(
                "onvif.utils.discovery.ONVIFClient",
                return_value=client,
            ),
            patch(
                "onvif.utils.discovery.safe_call",
                side_effect=[None, None],
            ),
        ):
            result = discovery._process_device([device])

        assert result[0]["hostname"] is None
        assert result[0]["date_time"] == {}
        assert result[0]["services"] == []

    def test_process_device_gets_hostname(self, discovery):
        """Test that _process_device retrieves and stores the device hostname."""
        device = {
            "host": "192.168.1.100",
            "port": 80,
        }

        client = Mock()
        client.services = []

        device_service = Mock()
        client.devicemgmt.return_value = device_service

        hostname = SimpleNamespace(Name="camera-01")

        with (
            patch(
                "onvif.utils.discovery.ONVIFClient",
                return_value=client,
            ),
            patch(
                "onvif.utils.discovery.safe_call",
                side_effect=[hostname, None],
            ),
        ):
            result = discovery._process_device([device])

        assert result[0]["hostname"] == "camera-01"

    def test_process_device_handles_hostname_failure(self, discovery):
        """Test that _process_device handles hostname retrieval failures."""
        device = {
            "host": "192.168.1.100",
            "port": 80,
        }

        client = Mock()
        client.services = []

        with (
            patch(
                "onvif.utils.discovery.ONVIFClient",
                return_value=client,
            ),
            patch(
                "onvif.utils.discovery.safe_call",
                side_effect=[
                    ONVIFOperationException(
                        "GetHostname failed",
                        RuntimeError("failed"),
                    ),
                    None,
                ],
            ),
        ):
            result = discovery._process_device([device])

        assert result[0]["hostname"] is None

    def test_process_device_gets_date_time(self, discovery):
        """Test that _process_device retrieves and formats device date and time."""
        device = {
            "host": "192.168.1.100",
            "port": 80,
        }

        client = Mock()
        client.services = []

        device_service = Mock()
        client.devicemgmt.return_value = device_service

        utc = SimpleNamespace(
            Date=SimpleNamespace(Year=2026, Month=10, Day=3),
            Time=SimpleNamespace(Hour=12, Minute=34, Second=56),
        )
        local = SimpleNamespace(
            Date=SimpleNamespace(Year=2026, Month=10, Day=3),
            Time=SimpleNamespace(Hour=19, Minute=34, Second=56),
        )

        date_time = SimpleNamespace(
            UTCDateTime=utc,
            LocalDateTime=local,
        )

        with (
            patch(
                "onvif.utils.discovery.ONVIFClient",
                return_value=client,
            ),
            patch(
                "onvif.utils.discovery.safe_call",
                side_effect=[None, date_time],
            ),
        ):
            result = discovery._process_device([device])

        assert result[0]["date_time"] == {
            "utc": "2026-10-03T12:34:56",
            "local": "2026-10-03T19:34:56",
        }

    def test_process_device_handles_missing_date_time(self, discovery):
        """Test that _process_device handles date/time retrieval failures."""
        device = {
            "host": "192.168.1.100",
            "port": 80,
        }

        client = Mock()
        client.services = []

        with (
            patch(
                "onvif.utils.discovery.ONVIFClient",
                return_value=client,
            ),
            patch(
                "onvif.utils.discovery.safe_call",
                side_effect=[
                    None,
                    ONVIFOperationException(
                        "GetSystemDateAndTime failed",
                        RuntimeError("failed"),
                    ),
                ],
            ),
        ):
            result = discovery._process_device([device])

        assert result[0]["date_time"] == {}

    def test_process_device_adds_known_services(self, discovery):
        """Test that _process_device identifies services using the ONVIF namespace
        map."""
        device = {
            "host": "192.168.1.100",
            "port": 80,
        }

        service = SimpleNamespace(
            Namespace="urn:test:device",
        )

        client = Mock()
        client.services = [service]

        with (
            patch(
                "onvif.utils.discovery.ONVIFClient",
                return_value=client,
            ),
            patch(
                "onvif.utils.discovery.ONVIF_NAMESPACE_MAP",
                {
                    "urn:test:device": [
                        ("devicemgmt",),
                    ],
                },
            ),
            patch(
                "onvif.utils.discovery.safe_call",
                side_effect=[None, None],
            ),
        ):
            result = discovery._process_device([device])

        assert result[0]["services"] == ["devicemgmt"]

    def test_process_device_adds_unknown_service(self, discovery):
        """Test that _process_device labels services with unknown namespaces."""
        device = {
            "host": "192.168.1.100",
            "port": 80,
        }

        service = SimpleNamespace(
            Namespace="urn:test:unknown",
        )

        client = Mock()
        client.services = [service]

        with (
            patch(
                "onvif.utils.discovery.ONVIFClient",
                return_value=client,
            ),
            patch(
                "onvif.utils.discovery.ONVIF_NAMESPACE_MAP",
                {},
            ),
            patch(
                "onvif.utils.discovery.safe_call",
                side_effect=[None, None],
            ),
        ):
            result = discovery._process_device([device])

        assert result[0]["services"] == [
            "unknown(urn:test:unknown)",
        ]

    def test_process_device_skips_device_when_connection_fails(self, discovery):
        """Test that _process_device handles ONVIF client connection failures."""
        device = {
            "host": "192.168.1.100",
            "port": 80,
        }

        error = ONVIFOperationException(
            "Connection failed",
            RuntimeError("connection failed"),
        )

        with patch(
            "onvif.utils.discovery.ONVIFClient",
            side_effect=error,
        ):
            result = discovery._process_device([device])

        assert result[0]["hostname"] is None
        assert result[0]["date_time"] == {}
        assert result[0]["services"] == []

    def test_process_device_passes_host_and_port_without_auth(self, discovery):
        """Test that _process_device creates the ONVIF client with the device
        endpoint."""
        device = {
            "host": "192.168.1.100",
            "port": 8080,
        }

        client = Mock()
        client.services = []

        with (
            patch(
                "onvif.utils.discovery.ONVIFClient",
                return_value=client,
            ) as mock_client,
            patch(
                "onvif.utils.discovery.safe_call",
                side_effect=[None, None],
            ),
        ):
            discovery._process_device([device])

        mock_client.assert_called_once_with(
            host="192.168.1.100",
            port=8080,
        )


class TestDiscover:
    """Tests for the discover method of ONVIFDiscovery."""

    def test_discover_socket_failure_returns_empty_list(self, discovery):
        """Test that discover returns an empty list when socket creation fails."""
        with (
            patch.object(
                discovery,
                "get_local_ip",
                return_value="192.168.1.10",
            ),
            patch(
                "onvif.utils.discovery.socket.socket",
                side_effect=OSError("socket failed"),
            ),
        ):
            assert discovery.discover() == []

    def test_discover_sends_probe_and_processes_responses(self, discovery):
        """Test that discover sends a WS-Discovery probe and processes responses."""
        sock = Mock()

        sock.recvfrom.side_effect = [
            (
                b'<?xml version="1.0"?><ProbeMatch></ProbeMatch>',
                ("192.168.1.100", 3702),
            ),
            socket_timeout(),
        ]

        parsed_devices = [
            {
                "host": "192.168.1.100",
                "port": 80,
            }
        ]

        with (
            patch.object(
                discovery,
                "get_local_ip",
                return_value="192.168.1.10",
            ),
            patch(
                "onvif.utils.discovery.socket.socket",
                return_value=sock,
            ),
            patch(
                "onvif.utils.discovery.uuid.uuid4",
                return_value="test-uuid",
            ),
            patch.object(
                discovery,
                "_parse_responses",
                return_value=parsed_devices,
            ) as parse_responses,
            patch.object(
                discovery,
                "_process_device",
                side_effect=lambda devices: devices,
            ) as process_device,
        ):
            result = discovery.discover()

        assert result == parsed_devices

        sock.bind.assert_called_once_with(("192.168.1.10", 0))
        sock.settimeout.assert_called_once_with(discovery.timeout)
        sock.sendto.assert_called_once()

        sent_data, destination = sock.sendto.call_args.args

        assert b"test-uuid" in sent_data
        assert destination == (
            discovery.WS_DISCOVERY_ADDRESS_IPV4,
            discovery.WS_DISCOVERY_PORT,
        )

        parse_responses.assert_called_once()
        process_device.assert_called_once_with(parsed_devices)

        sock.close.assert_called_once()

    def test_discover_uses_empty_bind_address_when_local_ip_is_empty(
        self,
        discovery,
    ):
        """Test that discover binds to an empty address when no local IP is
        available."""
        sock = Mock()
        sock.recvfrom.side_effect = [socket_timeout()]

        with (
            patch.object(
                discovery,
                "get_local_ip",
                return_value="",
            ),
            patch(
                "onvif.utils.discovery.socket.socket",
                return_value=sock,
            ),
            patch(
                "onvif.utils.discovery.uuid.uuid4",
                return_value="test-uuid",
            ),
            patch.object(
                discovery,
                "_parse_responses",
                return_value=[],
            ),
            patch.object(
                discovery,
                "_process_device",
                side_effect=lambda devices: devices,
            ),
        ):
            result = discovery.discover()

        assert result == []
        sock.bind.assert_called_once_with(("", 0))

    def test_discover_applies_search_filter(self, discovery):
        """Test that discover applies the requested device search filter."""
        sock = Mock()
        sock.recvfrom.side_effect = [socket_timeout()]

        devices = [
            {
                "host": "192.168.1.100",
                "types": ["Camera"],
                "scopes": [],
            }
        ]

        filtered = [devices[0]]

        with (
            patch.object(
                discovery,
                "get_local_ip",
                return_value="192.168.1.10",
            ),
            patch(
                "onvif.utils.discovery.socket.socket",
                return_value=sock,
            ),
            patch.object(
                discovery,
                "_parse_responses",
                return_value=devices,
            ),
            patch.object(
                discovery,
                "_filter_devices",
                return_value=filtered,
            ) as filter_devices,
            patch.object(
                discovery,
                "_process_device",
                side_effect=lambda devices: devices,
            ),
        ):
            result = discovery.discover(search="camera")

        assert result == filtered
        filter_devices.assert_called_once_with(
            devices,
            "camera",
        )

    def test_discover_ignores_malformed_packets(self, discovery):
        """Test that discover ignores malformed WS-Discovery packets."""
        sock = Mock()

        sock.recvfrom.side_effect = [
            (b"not valid xml but long enough", ("192.168.1.100", 3702)),
            socket_timeout(),
        ]

        with (
            patch.object(
                discovery,
                "get_local_ip",
                return_value="192.168.1.10",
            ),
            patch(
                "onvif.utils.discovery.socket.socket",
                return_value=sock,
            ),
            patch.object(
                discovery,
                "_parse_responses",
                return_value=[],
            ),
            patch.object(
                discovery,
                "_process_device",
                side_effect=lambda devices: devices,
            ),
        ):
            result = discovery.discover()

        assert result == []


class TestDiscoveryConstants:
    """Tests for the constants defined in ONVIFDiscovery."""

    def test_discovery_constants(self):
        """Test that the WS-Discovery network constants have the expected values."""
        assert ONVIFDiscovery.WS_DISCOVERY_PORT == 3702
        assert ONVIFDiscovery.WS_DISCOVERY_ADDRESS_IPV4 == "239.255.255.250"

    def test_probe_message_contains_required_ws_discovery_fields(self):
        """Test that the WS-Discovery probe template contains required fields."""
        probe = ONVIFDiscovery.WS_DISCOVERY_PROBE_MESSAGE

        assert "http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe" in probe
        assert "urn:uuid:{uuid}" in probe
        assert "urn:schemas-xmlsoap-org:ws:2005:04:discovery" in probe


# Socket modules


def discovery_module_socket_af_inet():
    """Return the IPv4 address-family constant used by the discovery socket."""
    return socket.AF_INET


def discovery_module_socket_dgram():
    """Return the UDP datagram socket type used by the discovery socket."""
    return socket.SOCK_DGRAM


def discovery_socket_sol_socket():
    """Return the socket-level option constant used for socket configuration."""
    return socket.SOL_SOCKET


def discovery_socket_so_reuseaddr():
    """Return the socket option constant for enabling address reuse."""
    return socket.SO_REUSEADDR


def discovery_socket_ipproto_ip():
    """Return the IP protocol level constant used for socket options."""
    return socket.IPPROTO_IP


def discovery_socket_ip_multicast_ttl():
    """Return the socket option constant for configuring multicast TTL."""
    return socket.IP_MULTICAST_TTL


def socket_timeout():
    """Return a socket timeout exception for simulating receive timeouts."""
    return socket.timeout()
