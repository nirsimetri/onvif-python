"""Tests for ONVIF CLI utility functions."""

import ctypes
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

import onvif.cli.utils as cli_utils
from onvif.cli.utils import (
    _colors_enabled,
    _is_valid_json,
    colorize,
    format_capabilities_as_services,
    format_services_list,
    get_device_available_services,
    get_service_methods,
    get_service_required_args,
    parse_json_params,
)


class TestIsValidJson:
    """Tests for validating JSON strings."""

    @pytest.mark.parametrize(
        "value",
        [
            "{}",
            "[]",
            '{"foo": "bar"}',
            '{"foo": 123}',
            "true",
            "false",
            "null",
            "123",
            '"hello"',
        ],
    )
    def test_valid(self, value):
        """Test valid JSON strings."""
        assert _is_valid_json(value) is True

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "hello",
            "foo=bar",
            "{invalid}",
            '{"foo":}',
            "[1, 2,",
        ],
    )
    def test_invalid(self, value):
        """Test invalid JSON strings."""
        assert _is_valid_json(value) is False


class TestParseJsonParams:
    """Tests for parsing CLI JSON and key-value parameters."""

    def test_empty(self):
        """Test empty parameter input."""
        assert parse_json_params("") == {}
        assert parse_json_params("   ") == {}

    def test_json_object(self):
        """Test parsing a complete JSON object."""
        params = parse_json_params('{"a": 1, "b": "hello"}')

        assert params == {
            "a": 1,
            "b": "hello",
        }

    def test_json_array(self):
        """Test parsing JSON values as parameters."""
        params = parse_json_params('{"items": [1, 2, 3]}')

        assert params == {
            "items": [1, 2, 3],
        }

    def test_key_value_pairs(self):
        """Test parsing space-separated key=value parameters."""
        params = parse_json_params("foo=bar count=10 enabled=true")

        assert params == {
            "foo": "bar",
            "count": 10,
            "enabled": True,
        }

    def test_comma_separated(self):
        """Test parsing comma-separated key=value parameters."""
        params = parse_json_params("foo=bar,count=10,enabled=true")

        assert params == {
            "foo": "bar",
            "count": 10,
            "enabled": True,
        }

    def test_mixed_separators(self):
        """Test parsing parameters separated by spaces and commas."""
        params = parse_json_params("foo=bar, count=10 enabled=false")

        assert params == {
            "foo": "bar",
            "count": 10,
            "enabled": False,
        }

    def test_string_with_spaces(self):
        """Test quoted string values containing spaces."""
        params = parse_json_params('name="John Doe"')

        assert params == {
            "name": "John Doe",
        }

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("true", True),
            ("TRUE", True),
            ("false", False),
            ("FALSE", False),
            ("none", None),
            ("None", None),
            ("null", None),
            ("NULL", None),
        ],
    )
    def test_special_values(self, value, expected):
        """Test boolean and null-like values."""
        assert parse_json_params(f"value={value}") == {"value": expected}

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("10", 10),
            ("-10", -10),
            ("3.14", 3.14),
            ("-3.14", -3.14),
        ],
    )
    def test_numeric_values(self, value, expected):
        """Test integer and floating-point conversion."""
        assert parse_json_params(f"value={value}") == {"value": expected}

    def test_nested_json_object(self):
        """Test JSON objects as key=value values."""
        params = parse_json_params('config={"name":"camera","enabled":true}')

        assert params == {
            "config": {
                "name": "camera",
                "enabled": True,
            }
        }

    def test_nested_json_object_with_spaces(self):
        """Test nested JSON objects containing spaces."""
        params = parse_json_params('config={"name": "camera", "enabled": true}')

        assert params == {
            "config": {
                "name": "camera",
                "enabled": True,
            }
        }

    def test_nested_json_array(self):
        """Test JSON arrays as key=value values."""
        params = parse_json_params("items=[1, 2, 3]")

        assert params == {
            "items": [1, 2, 3],
        }

    def test_unquoted_json_keys(self):
        """Test fixing JSON objects with unquoted keys."""
        params = parse_json_params('config={"name":"camera","enabled":true}')

        assert params == {
            "config": {
                "name": "camera",
                "enabled": True,
            }
        }

    def test_quoted_json_string(self):
        """Test quoted JSON string values."""
        params = parse_json_params("value='\"hello\"'")

        assert params == {
            "value": "hello",
        }

    def test_string_fallback(self):
        """Test fallback to a plain string."""
        params = parse_json_params("value=hello")

        assert params == {
            "value": "hello",
        }

    def test_key_with_quotes(self):
        """Test stripping quotes from parameter keys."""
        params = parse_json_params('"foo"=bar')

        assert params == {
            "foo": "bar",
        }

    def test_value_with_equals(self):
        """Test values containing an equals sign."""
        params = parse_json_params("url=http://example.com?a=b")

        assert params == {
            "url": "http://example.com?a=b",
        }


class TestGetServiceRequiredArgs:
    """Tests for determining required service arguments."""

    @pytest.mark.parametrize(
        "service_name",
        [
            "pullpoint",
            "subscription",
        ],
    )
    def test_requires_subscription_ref(self, service_name):
        """Test services requiring SubscriptionRef."""
        assert get_service_required_args(service_name) == ["SubscriptionRef"]

    @pytest.mark.parametrize(
        "service_name",
        [
            "devicemgmt",
            "events",
            "media",
            "media2",
            "ptz",
            "analytics",
            "search",
            "recording",
            "replay",
            "unknown",
            "",
        ],
    )
    def test_no_required_args(self, service_name):
        """Test services without required arguments."""
        assert get_service_required_args(service_name) is None


# pylint: disable=too-few-public-methods
class TestGetServiceMethods:
    """Tests for extracting callable public service methods."""

    def test_returns_public_callable_methods(self):
        """Test extracting callable public service methods."""
        service = Mock()

        # Mock needs explicit attributes because dir(Mock) contains many helpers.
        service.GetProfiles = Mock()
        service.GetStreamUri = Mock()
        service._private_method = Mock()  # pylint: disable=protected-access
        service.type = Mock()
        service.desc = Mock()
        service.operations = Mock()
        service.to_dict = Mock()
        service.some_value = "not callable"

        methods = get_service_methods(service)

        assert "GetProfiles" in methods
        assert "GetStreamUri" in methods
        assert "some_value" not in methods
        assert "_private_method" not in methods
        assert "type" not in methods
        assert "desc" not in methods
        assert "operations" not in methods
        assert "to_dict" not in methods

        assert methods == sorted(methods)


class TestColorsEnabled:
    """Tests for detecting terminal ANSI color support."""

    def test_non_windows(self):
        """Test that ANSI colors are enabled on non-Windows systems."""
        _colors_enabled.cache_clear()

        with patch("onvif.cli.utils.os.name", "posix"):
            assert _colors_enabled() is True

        _colors_enabled.cache_clear()

    def test_windows_success(self):
        """Test enabling ANSI colors on Windows."""
        _colors_enabled.cache_clear()

        kernel32 = Mock()
        kernel32.GetStdHandle.return_value = 123
        kernel32.GetConsoleMode.return_value = True
        kernel32.SetConsoleMode.return_value = True

        windll = Mock()
        windll.kernel32 = kernel32

        with (
            patch.object(cli_utils.os, "name", "nt"),
            patch.object(ctypes, "windll", windll, create=True),
        ):
            assert _colors_enabled() is True

        kernel32.SetConsoleMode.assert_called_once()
        _colors_enabled.cache_clear()

    @pytest.mark.parametrize(
        "exception",
        [
            AttributeError(),
            OSError(),
        ],
    )
    def test_windows_failure(self, exception):
        """Test Windows ANSI detection failure."""

        class FakeWindll:  # pylint: disable=too-few-public-methods
            """Fake ctypes.windll for testing."""

            @property
            def kernel32(self):
                """Return a fake kernel32 object that raises an exception."""
                raise exception

        _colors_enabled.cache_clear()

        with (
            patch("onvif.cli.utils.os.name", "nt"),
            patch(
                "onvif.cli.utils.ctypes.windll",
                FakeWindll(),
                create=True,
            ),
        ):
            assert _colors_enabled() is False

        _colors_enabled.cache_clear()


class TestColorize:
    """Tests for applying ANSI colors to text."""

    def test_when_colors_disabled(self):
        """Test colorize without ANSI colors."""
        with patch(
            "onvif.cli.utils._colors_enabled",
            return_value=False,
        ):
            assert colorize("hello", "red") == "hello"

    def test_when_colors_enabled(self):
        """Test colorize with ANSI colors."""
        with patch(
            "onvif.cli.utils._colors_enabled",
            return_value=True,
        ):
            assert colorize("hello", "red") == "\033[91mhello\033[0m"

    def test_unknown_color(self):
        """Test colorize with an unknown color name."""
        with patch(
            "onvif.cli.utils._colors_enabled",
            return_value=True,
        ):
            assert colorize("hello", "unknown") == "hello\033[0m"


class TestFormatCapabilitiesAsServices:
    """Tests for formatting device capabilities as service entries."""

    def test_empty(self):
        """Test formatting capabilities without services."""
        capabilities = SimpleNamespace()

        result = format_capabilities_as_services(capabilities)

        assert "No services found in capabilities" in result

    def test_standard_services(self):
        """Test formatting standard capability services."""
        capabilities = SimpleNamespace(
            Device={"XAddr": "http://192.168.1.17/onvif/device"},
            Analytics={"XAddr": "http://192.168.1.17/onvif/analytics"},
            Events={"XAddr": "http://192.168.1.17/onvif/events"},
            Imaging={"XAddr": "http://192.168.1.17/onvif/imaging"},
            Media={"XAddr": "http://192.168.1.17/onvif/media"},
            PTZ={"XAddr": "http://192.168.1.17/onvif/ptz"},
        )

        result = format_capabilities_as_services(capabilities)

        for service_name in [
            "devicemgmt",
            "analytics",
            "events",
            "imaging",
            "media",
            "ptz",
        ]:
            assert service_name in result

        assert "http://192.168.1.17/onvif/device" in result
        assert "http://192.168.1.17/onvif/media" in result

    def test_ignores_capability_without_xaddr(self):
        """Test that capabilities without XAddr are skipped."""
        capabilities = SimpleNamespace(
            Device={},
            Media={"Other": "value"},
            PTZ={"XAddr": "http://example.com/ptz"},
        )

        result = format_capabilities_as_services(capabilities)

        assert "ptz" in result
        assert "devicemgmt" not in result
        assert "media" not in result

    def test_extension(self):
        """Test first-level extension capabilities."""
        extension = SimpleNamespace(
            DeviceIO={"XAddr": "http://example.com/deviceio"},
            Display={"XAddr": "http://example.com/display"},
            Recording={"XAddr": "http://example.com/recording"},
            Search={"XAddr": "http://example.com/search"},
            Replay={"XAddr": "http://example.com/replay"},
            Receiver={"XAddr": "http://example.com/receiver"},
            AnalyticsDevice={"XAddr": "http://example.com/analyticsdevice"},
        )

        capabilities = SimpleNamespace(
            Extension=extension,
        )

        result = format_capabilities_as_services(capabilities)

        for service_name in [
            "deviceio",
            "display",
            "recording",
            "search",
            "replay",
            "receiver",
            "analyticsdevice",
        ]:
            assert service_name in result

    def test_nested_extension(self):
        """Test second-level extension capabilities."""
        nested = SimpleNamespace(
            AccessControl={"XAddr": "http://example.com/accesscontrol"},
            DoorControl={"XAddr": "http://example.com/doorcontrol"},
            AccessRules={"XAddr": "http://example.com/accessrules"},
            ActionEngine={"XAddr": "http://example.com/actionengine"},
            AppManagement={"XAddr": "http://example.com/appmgmt"},
            AuthenticationBehavior={
                "XAddr": "http://example.com/authenticationbehavior"
            },
            Credential={"XAddr": "http://example.com/credential"},
            Provisioning={"XAddr": "http://example.com/provisioning"},
            Schedule={"XAddr": "http://example.com/schedule"},
            Thermal={"XAddr": "http://example.com/thermal"},
            Uplink={"XAddr": "http://example.com/uplink"},
            Security={"XAddr": "http://example.com/security"},
        )

        capabilities = SimpleNamespace(
            Extension=SimpleNamespace(
                Extensions=nested,
            )
        )

        result = format_capabilities_as_services(capabilities)

        for service_name in [
            "accesscontrol",
            "doorcontrol",
            "accessrules",
            "actionengine",
            "appmgmt",
            "authenticationbehavior",
            "credential",
            "provisioning",
            "schedule",
            "thermal",
            "uplink",
            "advancedsecurity",
        ]:
            assert service_name in result


class TestFormatServicesList:
    """Tests for formatting ONVIF service lists."""

    def test_empty(self):
        """Test formatting an empty service list."""
        assert "No services available" in format_services_list([])

    def test_unknown_namespace(self):
        """Test formatting an unknown service namespace."""
        service = SimpleNamespace(
            Namespace="http://example.com/unknown",
            XAddr="http://192.168.1.17/onvif/unknown",
            Version={},
        )

        result = format_services_list([service])

        assert "unknown(http://example.com/unknown)" in result
        assert "http://192.168.1.17/onvif/unknown" in result
        assert "http://example.com/unknown" in result

    def test_single_binding(self):
        """Test formatting a known single-binding service."""
        service = SimpleNamespace(
            Namespace="http://www.onvif.org/ver10/media/wsdl",
            XAddr="http://192.168.1.17/onvif/Media",
            Version=SimpleNamespace(
                Major=1,
                Minor=2,
            ),
        )

        result = format_services_list([service])

        assert "media" in result
        assert "http://192.168.1.17/onvif/Media" in result
        assert "MediaBinding" in result
        assert "Version" in result
        assert "1.2" in result

    def test_single_binding_major_only(self):
        """Test formatting a service with only a major version."""
        service = SimpleNamespace(
            Namespace="http://www.onvif.org/ver10/media/wsdl",
            XAddr="http://192.168.1.17/onvif/Media",
            Version=SimpleNamespace(
                Major=1,
                Minor="",
            ),
        )

        result = format_services_list([service])

        assert "Version" in result
        assert "1" in result

    def test_multi_binding(self):
        """Test formatting a multi-binding service."""
        service = SimpleNamespace(
            Namespace="http://www.onvif.org/ver10/events/wsdl",
            XAddr="http://192.168.1.17/onvif/Events",
            Version=SimpleNamespace(
                Major=2,
                Minor=0,
            ),
        )

        result = format_services_list([service])

        assert "events" in result
        assert "EventBinding" in result
        assert "pullpoint" in result
        assert "PullPointSubscriptionBinding" in result
        assert "notification" in result
        assert "NotificationProducerBinding" in result
        assert "subscription" in result
        assert "SubscriptionManagerBinding" in result

    def test_without_version(self):
        """Test formatting a service without version information."""
        service = SimpleNamespace(
            Namespace="http://www.onvif.org/ver10/media/wsdl",
            XAddr="http://192.168.1.17/onvif/Media",
            Version=None,
        )

        result = format_services_list([service])

        assert "media" in result
        assert "MediaBinding" in result
        assert "Version" not in result


class TestGetDeviceAvailableServices:
    """Tests for determining services available from an ONVIF client."""

    def test_always_includes_devicemgmt(self):
        """Test that devicemgmt is always available."""
        client = SimpleNamespace(
            services=[],
            capabilities=None,
        )

        result = get_device_available_services(client)

        assert result == ["devicemgmt"]

    def test_from_services(self):
        """Test service discovery from GetServices data."""
        events = SimpleNamespace(
            Namespace="http://www.onvif.org/ver10/events/wsdl",
        )
        media = SimpleNamespace(
            Namespace="http://www.onvif.org/ver10/media/wsdl",
        )
        ptz = SimpleNamespace(
            Namespace="http://www.onvif.org/ver20/ptz/wsdl",
        )

        client = SimpleNamespace(
            services=[events, media, ptz],
            capabilities=None,
        )

        result = get_device_available_services(client)

        assert result == sorted(
            {
                "devicemgmt",
                "events",
                "pullpoint",
                "notification",
                "subscription",
                "media",
                "ptz",
            }
        )

    def test_ignores_unknown_namespace(self):
        """Test that unknown service namespaces are ignored."""
        client = SimpleNamespace(
            services=[
                SimpleNamespace(
                    Namespace="http://example.com/unknown",
                ),
            ],
            capabilities=None,
        )

        result = get_device_available_services(client)

        assert result == ["devicemgmt"]

    def test_from_capabilities(self):
        """Test capability-based service detection."""
        capabilities = SimpleNamespace(
            Analytics=True,
            Events=True,
            Imaging=True,
            Media=True,
            PTZ=True,
        )

        client = SimpleNamespace(
            services=[],
            capabilities=capabilities,
        )

        result = get_device_available_services(client)

        assert result == sorted(
            {
                "devicemgmt",
                "analytics",
                "ruleengine",
                "events",
                "pullpoint",
                "notification",
                "subscription",
                "imaging",
                "media",
                "ptz",
            }
        )

    def test_extension_capabilities(self):
        """Test first-level extension capability detection."""
        extension = SimpleNamespace(
            DeviceIO=True,
            Display=True,
            Recording=True,
            Search=True,
            Replay=True,
            Receiver=True,
            AnalyticsDevice=True,
        )

        capabilities = SimpleNamespace(
            Analytics=None,
            Events=None,
            Imaging=None,
            Media=None,
            PTZ=None,
            Extension=extension,
        )

        client = SimpleNamespace(
            services=[],
            capabilities=capabilities,
        )

        result = get_device_available_services(client)

        assert result == sorted(
            {
                "devicemgmt",
                "deviceio",
                "display",
                "recording",
                "search",
                "replay",
                "receiver",
                "analyticsdevice",
            }
        )

    def test_nested_extension_capabilities(self):
        """Test second-level extension capability detection."""
        nested = SimpleNamespace(
            AccessControl=True,
            DoorControl=True,
            AccessRules=True,
            ActionEngine=True,
            AppManagement=True,
            AuthenticationBehavior=True,
            Credential=True,
            Provisioning=True,
            Schedule=True,
            Thermal=True,
            Uplink=True,
            Security=True,
        )

        capabilities = SimpleNamespace(Extension=SimpleNamespace(Extensions=nested))

        client = SimpleNamespace(
            services=[],
            capabilities=capabilities,
        )

        result = get_device_available_services(client)

        assert result == sorted(
            {
                "devicemgmt",
                "accesscontrol",
                "doorcontrol",
                "accessrules",
                "actionengine",
                "appmgmt",
                "authenticationbehavior",
                "credential",
                "provisioning",
                "schedule",
                "thermal",
                "uplink",
                "security",
                "jwt",
                "keystore",
                "tlsserver",
                "dot1x",
                "authorizationserver",
                "mediasigning",
            }
        )

    def test_deduplicates_services(self):
        """Test that duplicate services are removed."""
        media = SimpleNamespace(
            Namespace="http://www.onvif.org/ver10/media/wsdl",
        )

        capabilities = SimpleNamespace(
            Media=True,
        )

        client = SimpleNamespace(
            services=[media],
            capabilities=capabilities,
        )

        # Because services takes precedence over capabilities, only the
        # service-derived result is expected here.
        result = get_device_available_services(client)

        assert result == ["devicemgmt", "media"]
