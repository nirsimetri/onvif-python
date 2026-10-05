"""Tests for ONVIFOperator."""

import os
from unittest.mock import Mock, patch

import pytest
from zeep.exceptions import Fault

from onvif.operator import CacheMode, ONVIFOperator
from onvif.utils.exceptions import ONVIFOperationException


def make_operator(**attrs):
    """Create an ONVIFOperator without executing __init__."""
    operator = ONVIFOperator.__new__(ONVIFOperator)

    defaults = {
        "wsdl_path": "test.wsdl",
        "host": "192.168.1.100",
        "port": 80,
        "username": None,
        "password": None,
        "http_digest": False,
        "timeout": 10,
        "apply_patch": True,
        "address": "http://192.168.1.100:80/onvif/device_service",
        "service_name": "Device",
    }
    defaults.update(attrs)

    for key, value in defaults.items():
        setattr(operator, key, value)

    return operator


class TestCacheMode:
    """Test for CacheMode enum."""

    def test_cache_mode_values(self):
        """Test that CacheMode enum values are correct."""
        assert CacheMode.NONE.value == "none"
        assert CacheMode.MEM.value == "mem"
        assert CacheMode.DB.value == "db"

    def test_cache_mode_members(self):
        """Test that CacheMode enum members are correct."""
        assert list(CacheMode) == [
            CacheMode.NONE,
            CacheMode.MEM,
            CacheMode.DB,
        ]


class TestONVIFOperatorInitialization:
    """Test ONVIFOperator initialization and configuration."""

    @pytest.mark.parametrize(
        ("cache", "cache_class"),
        [
            (CacheMode.NONE, None),
            (CacheMode.MEM, "InMemoryCache"),
            (CacheMode.DB, "SqliteCache"),
        ],
    )
    def test_init_cache_modes(self, cache, cache_class):
        """Test that ONVIFOperator initializes with different cache modes."""
        mock_session = Mock()
        mock_client = Mock()
        mock_transport = Mock()

        patches = {
            "session": patch(
                "onvif.operator.requests.Session",
                return_value=mock_session,
            ),
            "transport": patch(
                "onvif.operator.Transport",
                return_value=mock_transport,
            ),
            "client": patch(
                "onvif.operator.Client",
                return_value=mock_client,
            ),
        }

        with (
            patches["session"] as mock_session_cls,
            patches["transport"] as mock_transport_cls,
            patches["client"] as mock_client_cls,
            patch("onvif.operator.Settings"),
            patch("onvif.operator.InMemoryCache") as mock_memory_cache,
            patch("onvif.operator.SqliteCache") as mock_sqlite_cache,
            patch.object(
                ONVIFOperator,
                "_create_wsse",
                return_value=None,
            ),
            patch("onvif.operator.os.makedirs"),
        ):
            operator = ONVIFOperator(
                wsdl_path="test.wsdl",
                host="192.168.1.100",
                port=80,
                binding="{urn:test}DeviceBinding",
                cache=cache,
                cache_path="/tmp/test-cache.sqlite",
            )

        assert operator.address == ("http://192.168.1.100:80/onvif/device_service")
        assert operator.service_name == "Device"
        mock_session_cls.assert_called_once_with()

        if cache_class == "InMemoryCache":
            mock_memory_cache.assert_called_once_with()
            mock_sqlite_cache.assert_not_called()
        elif cache_class == "SqliteCache":
            mock_sqlite_cache.assert_called_once_with(path="/tmp/test-cache.sqlite")
            mock_memory_cache.assert_not_called()
        else:
            mock_memory_cache.assert_not_called()
            mock_sqlite_cache.assert_not_called()

        mock_transport_cls.assert_called_once()
        mock_client_cls.assert_called_once()

    def test_init_uses_https_and_custom_service_path(self):
        """Test that ONVIFOperator initializes with HTTPS and a custom service path."""
        mock_session = Mock()
        mock_client = Mock()

        with (
            patch(
                "onvif.operator.requests.Session",
                return_value=mock_session,
            ),
            patch("onvif.operator.Transport"),
            patch(
                "onvif.operator.Client",
                return_value=mock_client,
            ),
            patch("onvif.operator.Settings"),
            patch.object(
                ONVIFOperator,
                "_create_wsse",
                return_value=None,
            ),
        ):
            operator = ONVIFOperator(
                wsdl_path="test.wsdl",
                host="camera.local",
                port=443,
                binding="{urn:test}MediaBinding",
                service_path="media_service",
                cache=CacheMode.NONE,
                use_https=True,
            )

        assert operator.address == ("https://camera.local:443/onvif/media_service")
        assert operator.service_name == "Media"

    def test_init_uses_explicit_xaddr(self):
        """Test that ONVIFOperator initializes with an explicit XAddr."""
        mock_client = Mock()

        with (
            patch("onvif.operator.requests.Session"),
            patch("onvif.operator.Transport"),
            patch(
                "onvif.operator.Client",
                return_value=mock_client,
            ),
            patch("onvif.operator.Settings"),
            patch.object(
                ONVIFOperator,
                "_create_wsse",
                return_value=None,
            ),
        ):
            operator = ONVIFOperator(
                wsdl_path="test.wsdl",
                host="camera.local",
                port=80,
                binding="{urn:test}DeviceBinding",
                xaddr="http://camera.local/custom",
                cache=CacheMode.NONE,
            )

        assert operator.address == "http://camera.local/custom"

    def test_init_defaults_service_path_when_empty(self):
        """Test that ONVIFOperator defaults to the standard service path when
        service_path is None."""
        mock_client = Mock()

        with (
            patch("onvif.operator.requests.Session"),
            patch("onvif.operator.Transport"),
            patch(
                "onvif.operator.Client",
                return_value=mock_client,
            ),
            patch("onvif.operator.Settings"),
            patch.object(
                ONVIFOperator,
                "_create_wsse",
                return_value=None,
            ),
        ):
            operator = ONVIFOperator(
                wsdl_path="test.wsdl",
                host="camera.local",
                port=80,
                binding="{urn:test}DeviceBinding",
                service_path=None,
                cache=CacheMode.NONE,
            )

        assert operator.address.endswith("/onvif/device_service")

    def test_init_creates_default_db_cache_path(self):
        """Test that ONVIFOperator creates the default database cache path when
        CacheMode.DB is used."""
        mock_client = Mock()

        with (
            patch("onvif.operator.requests.Session"),
            patch("onvif.operator.Transport"),
            patch(
                "onvif.operator.Client",
                return_value=mock_client,
            ),
            patch("onvif.operator.Settings"),
            patch.object(
                ONVIFOperator,
                "_create_wsse",
                return_value=None,
            ),
            patch(
                "onvif.operator.os.path.expanduser",
                return_value="/home/test/.onvif-python",
            ),
            patch("onvif.operator.os.makedirs") as mock_makedirs,
            patch("onvif.operator.SqliteCache") as mock_cache,
        ):
            ONVIFOperator(
                wsdl_path="test.wsdl",
                host="camera.local",
                port=80,
                binding="{urn:test}DeviceBinding",
                cache=CacheMode.DB,
            )

        mock_makedirs.assert_called_once_with(
            "/home/test/.onvif-python",
            exist_ok=True,
        )
        mock_cache.assert_called_once_with(
            path=os.path.join(
                "/home/test/.onvif-python",
                "onvif_zeep_cache.sqlite",
            )
        )

    def test_init_raises_for_unknown_cache_mode(self):
        """Test that ONVIFOperator raises ValueError for an unknown cache mode."""
        unknown_cache = object()

        with pytest.raises(ValueError, match="Unknown cache option"):
            ONVIFOperator(
                wsdl_path="test.wsdl",
                host="camera.local",
                port=80,
                binding="{urn:test}DeviceBinding",
                cache=unknown_cache,
            )

    def test_init_raises_without_binding(self):
        """Test that ONVIFOperator raises ValueError when binding is None."""
        with (
            patch("onvif.operator.requests.Session"),
            patch("onvif.operator.Transport"),
            patch("onvif.operator.Client"),
            patch("onvif.operator.Settings"),
            patch.object(
                ONVIFOperator,
                "_create_wsse",
                return_value=None,
            ),
        ):
            with pytest.raises(
                ValueError,
                match="Bindings must be set according to the WSDL service",
            ):
                ONVIFOperator(
                    wsdl_path="test.wsdl",
                    host="camera.local",
                    port=80,
                    binding=None,
                    cache=CacheMode.NONE,
                )

    def test_init_passes_configuration_to_client(self):
        """Test that ONVIFOperator passes the correct configuration to the Zeep
        client."""
        mock_client = Mock()
        mock_wsse = Mock()
        mock_transport = Mock()
        mock_settings = Mock()

        with (
            patch("onvif.operator.requests.Session"),
            patch(
                "onvif.operator.Transport",
                return_value=mock_transport,
            ) as mock_transport_cls,
            patch(
                "onvif.operator.Settings",
                return_value=mock_settings,
            ) as mock_settings_cls,
            patch(
                "onvif.operator.Client",
                return_value=mock_client,
            ) as mock_client_cls,
            patch.object(
                ONVIFOperator,
                "_create_wsse",
                return_value=mock_wsse,
            ),
        ):
            operator = ONVIFOperator(
                wsdl_path="test.wsdl",
                host="camera.local",
                port=80,
                username="admin",
                password="secret",
                timeout=25,
                binding="{urn:test}DeviceBinding",
                cache=CacheMode.NONE,
                plugins=["plugin"],
            )

        mock_transport_cls.assert_called_once_with(
            session=mock_transport_cls.call_args.kwargs["session"],
            operation_timeout=25,
        )

        mock_settings_cls.assert_called_once_with(
            strict=False,
            xml_huge_tree=True,
        )

        mock_client_cls.assert_called_once_with(
            wsdl="test.wsdl",
            transport=mock_transport,
            settings=mock_settings,
            wsse=mock_wsse,
            plugins=["plugin"],
        )

        mock_client.create_service.assert_called_once_with(
            binding_name="{urn:test}DeviceBinding",
            address=operator.address,
        )


# pylint: disable=protected-access
class TestCreateSession:
    """Tests for the _create_session method of ONVIFOperator."""

    def test_create_session_sets_verify(self):
        """Test that ONVIFOperator creates a requests.Session with the correct SSL
        verification setting."""
        operator = make_operator()

        with patch("onvif.operator.requests.Session") as mock_session_cls:
            session = operator._create_session(verify_ssl=True)

        assert session.verify is True
        mock_session_cls.assert_called_once_with()

    def test_create_session_disables_ssl_verification(self):
        """Test that ONVIFOperator creates a requests.Session with SSL verification
        disabled."""
        operator = make_operator()

        with (patch("onvif.operator.warnings.simplefilter") as mock_filter,):
            session = operator._create_session(verify_ssl=False)

        assert session.verify is False

        mock_filter.assert_called_once_with(
            "once",
            __import__(
                "urllib3",
            ).exceptions.InsecureRequestWarning,
        )

    def test_create_session_configures_digest_auth(self):
        """Test that ONVIFOperator creates a requests.Session with HTTP Digest
        authentication when enabled."""
        operator = make_operator(
            username="admin",
            password="secret",
            http_digest=True,
        )

        with (patch("onvif.operator.HTTPDigestAuth") as mock_auth,):
            session = operator._create_session(verify_ssl=True)

        mock_auth.assert_called_once_with(
            username="admin",
            password="secret",
        )
        assert session.auth is mock_auth.return_value

    @pytest.mark.parametrize(
        ("http_digest", "username", "password"),
        [
            (False, "admin", "secret"),
            (True, None, "secret"),
            (True, "admin", None),
            (True, None, None),
        ],
    )
    def test_create_session_without_digest_auth(
        self,
        http_digest,
        username,
        password,
    ):
        """Test that ONVIFOperator creates a requests.Session without HTTP Digest
        authentication when not enabled or credentials are missing."""
        operator = make_operator(
            http_digest=http_digest,
            username=username,
            password=password,
        )

        with (patch("onvif.operator.HTTPDigestAuth") as mock_auth,):
            operator._create_session(verify_ssl=True)

        mock_auth.assert_not_called()


# pylint: disable=protected-access
class TestCreateWsse:
    """Tests for the _create_wsse method of ONVIFOperator."""

    def test_create_wsse_returns_none_for_http_digest(self):
        """Test that ONVIFOperator._create_wsse returns None when HTTP Digest
        authentication is enabled."""
        operator = make_operator(
            http_digest=True,
            username="admin",
            password="secret",
        )

        with patch("onvif.operator.UsernameToken") as mock_token:
            result = operator._create_wsse()

        assert result is None
        mock_token.assert_not_called()

    @pytest.mark.parametrize(
        ("username", "password"),
        [
            (None, None),
            ("admin", None),
            (None, "secret"),
        ],
    )
    def test_create_wsse_returns_none_without_credentials(
        self,
        username,
        password,
    ):
        """Test that ONVIFOperator._create_wsse returns None when username or password
        is missing."""
        operator = make_operator(
            http_digest=False,
            username=username,
            password=password,
        )

        with patch("onvif.operator.UsernameToken") as mock_token:
            result = operator._create_wsse()

        assert result is None
        mock_token.assert_not_called()

    def test_create_wsse_creates_username_token(self):
        """Test that ONVIFOperator._create_wsse creates a UsernameToken when HTTP Digest
        is disabled and credentials are provided."""
        operator = make_operator(
            http_digest=False,
            username="admin",
            password="secret",
        )

        with patch("onvif.operator.UsernameToken") as mock_token:
            result = operator._create_wsse()

        assert result is mock_token.return_value
        mock_token.assert_called_once_with(
            username="admin",
            password="secret",
            use_digest=True,
        )


class TestCall:
    """Tests for the call public method of ONVIFOperator."""

    def test_call_returns_service_result_and_flattens_result(self):
        """Test that ONVIFOperator.call returns the result from the service and flattens
        it using ZeepPatcher."""
        service = Mock()
        service.GetDeviceInformation.return_value = {"raw": "value"}

        operator = make_operator(
            service=service,
            apply_patch=True,
        )

        flattened = {"flattened": "value"}

        with patch(
            "onvif.operator.ZeepPatcher.flatten_xsd_any_fields",
            return_value=flattened,
        ) as mock_flatten:
            result = operator.call(
                "GetDeviceInformation",
                "arg",
                timeout=5,
            )

        assert result == flattened
        service.GetDeviceInformation.assert_called_once_with(
            "arg",
            timeout=5,
        )
        mock_flatten.assert_called_once_with(
            {"raw": "value"},
        )

    def test_call_skips_flatten_when_patch_disabled(self):
        """Test that ONVIFOperator.call skips flattening the result when apply_patch is
        False."""
        service = Mock()
        service.GetDeviceInformation.return_value = "result"

        operator = make_operator(
            service=service,
            apply_patch=False,
        )

        with patch(
            "onvif.operator.ZeepPatcher.flatten_xsd_any_fields",
        ) as mock_flatten:
            result = operator.call("GetDeviceInformation")

        assert result == "result"
        mock_flatten.assert_not_called()

    def test_call_wraps_missing_method(self):
        """Test that ONVIFOperator.call raises ONVIFOperationException when the service
        method is missing."""
        service = Mock(spec=[])

        operator = make_operator(
            service=service,
            apply_patch=False,
        )

        with pytest.raises(ONVIFOperationException) as exc_info:
            operator.call("GetDeviceInformation")

        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, AttributeError)

    def test_call_wraps_zeep_fault(self):
        """Test that ONVIFOperator.call raises ONVIFOperationException when the service
        method raises a Zeep Fault."""
        service = Mock()
        fault = Fault("SOAP fault")
        service.GetDeviceInformation.side_effect = fault

        operator = make_operator(
            service=service,
            apply_patch=False,
        )

        with pytest.raises(ONVIFOperationException) as exc_info:
            operator.call("GetDeviceInformation")

        assert exc_info.value.__cause__ is fault

    def test_call_wraps_generic_exception(self):
        """Test that ONVIFOperator.call raises ONVIFOperationException when the service
        method raises a generic exception."""
        service = Mock()
        error = RuntimeError("connection failed")
        service.GetDeviceInformation.side_effect = error

        operator = make_operator(
            service=service,
            apply_patch=False,
        )

        with pytest.raises(ONVIFOperationException) as exc_info:
            operator.call("GetDeviceInformation")

        assert exc_info.value.__cause__ is error

    def test_call_passes_positional_and_keyword_arguments(self):
        """Test that ONVIFOperator.call correctly passes positional and keyword
        arguments to the service method."""
        service = Mock()
        service.GetProfiles.return_value = "result"

        operator = make_operator(
            service=service,
            apply_patch=False,
        )

        result = operator.call(
            "GetProfiles",
            "profile-token",
            timeout=30,
        )

        assert result == "result"
        service.GetProfiles.assert_called_once_with(
            "profile-token",
            timeout=30,
        )


class TestCreateType:
    """Tests for the create_type public method of ONVIFOperator."""

    def test_create_type_succeeds_with_first_namespace(self):
        """Test that ONVIFOperator.create_type successfully creates a type using the
        first namespace when available."""
        operator = make_operator()
        element = Mock()
        instance = Mock()

        element.return_value = instance
        operator.client = Mock()
        operator.client.get_element.return_value = element

        initialized = Mock()
        with patch.object(
            operator,
            "_initialize_nested_types",
            return_value=initialized,
        ) as mock_initialize:
            result = operator.create_type("GetProfiles")

        assert result is initialized
        operator.client.get_element.assert_called_once_with("ns0:GetProfiles")
        element.assert_called_once_with()
        mock_initialize.assert_called_once_with(instance)

    def test_create_type_tries_next_namespace_after_failure(self):
        """Test that ONVIFOperator.create_type tries the next namespace if the first one
        fails."""
        operator = make_operator()
        element = Mock()
        instance = Mock()

        element.return_value = instance

        def get_element(name):
            if name == "ns0:GetProfiles":
                raise ValueError("not found")
            return element

        operator.client = Mock()
        operator.client.get_element.side_effect = get_element

        with patch.object(
            operator,
            "_initialize_nested_types",
            return_value=instance,
        ):
            result = operator.create_type("GetProfiles")

        assert result is instance
        assert operator.client.get_element.call_count == 2
        assert operator.client.get_element.call_args_list[0].args == (
            "ns0:GetProfiles",
        )
        assert operator.client.get_element.call_args_list[1].args == ("tt:GetProfiles",)

    def test_create_type_falls_back_to_unqualified_element(self):
        """Test that ONVIFOperator.create_type falls back to an unqualified element if
        namespaced elements are not found."""
        operator = make_operator()
        element = Mock()
        instance = Mock()

        element.return_value = instance

        def get_element(name):
            if name in ("ns0:GetProfiles", "tt:GetProfiles"):
                raise AttributeError("not found")
            return element

        operator.client = Mock()
        operator.client.get_element.side_effect = get_element

        with patch.object(
            operator,
            "_initialize_nested_types",
            return_value=instance,
        ):
            result = operator.create_type("GetProfiles")

        assert result is instance
        assert operator.client.get_element.call_args_list[-1].args == ("GetProfiles",)

    def test_create_type_falls_back_to_namespaced_complex_type(self):
        """Test that ONVIFOperator.create_type falls back to a namespaced complex type
        if elements are not found."""
        operator = make_operator()
        type_obj = Mock()
        instance = Mock()

        type_obj.return_value = instance

        def get_element(name):
            raise AttributeError(name)

        def get_type(name):
            if name == "ns0:GetProfiles":
                return type_obj
            raise AttributeError(name)

        operator.client = Mock()
        operator.client.get_element.side_effect = get_element
        operator.client.get_type.side_effect = get_type

        with patch.object(
            operator,
            "_initialize_nested_types",
            return_value=instance,
        ):
            result = operator.create_type("GetProfiles")

        assert result is instance
        operator.client.get_type.assert_called_once_with("ns0:GetProfiles")

    def test_create_type_falls_back_to_second_complex_type_namespace(self):
        """Test that ONVIFOperator.create_type falls back to the second complex type
        namespace if the first one fails."""
        operator = make_operator()
        type_obj = Mock()
        instance = Mock()

        type_obj.return_value = instance

        def get_type(name):
            if name == "ns0:GetProfiles":
                raise ValueError("not found")
            if name == "tt:GetProfiles":
                return type_obj
            raise AttributeError(name)

        operator.client = Mock()
        operator.client.get_element.side_effect = AttributeError
        operator.client.get_type.side_effect = get_type

        with patch.object(
            operator,
            "_initialize_nested_types",
            return_value=instance,
        ):
            result = operator.create_type("GetProfiles")

        assert result is instance
        assert operator.client.get_type.call_args_list == [
            (("ns0:GetProfiles",),),
            (("tt:GetProfiles",),),
        ]

    def test_create_type_falls_back_to_unqualified_complex_type(self):
        """Test that ONVIFOperator.create_type falls back to an unqualified complex type
        if namespaced types are not found."""
        operator = make_operator()
        type_obj = Mock()
        instance = Mock()

        type_obj.return_value = instance

        operator.client = Mock()
        operator.client.get_element.side_effect = AttributeError
        operator.client.get_type.side_effect = lambda name: (
            type_obj
            if name == "GetProfiles"
            else (_ for _ in ()).throw(AttributeError(name))
        )

        with patch.object(
            operator,
            "_initialize_nested_types",
            return_value=instance,
        ):
            result = operator.create_type("GetProfiles")

        assert result is instance
        assert operator.client.get_type.call_args_list[-1].args == ("GetProfiles",)

    def test_create_type_raises_when_all_lookup_methods_fail(self):
        """Test that ONVIFOperator.create_type raises AttributeError when all lookup
        methods fail."""
        operator = make_operator()
        operator.client = Mock()
        operator.client.get_element.side_effect = AttributeError
        operator.client.get_type.side_effect = AttributeError

        with pytest.raises(
            AttributeError,
            match="Type 'GetProfiles' not found in WSDL schema",
        ):
            operator.create_type("GetProfiles")


# pylint: disable=invalid-name,unnecessary-pass,too-few-public-methods
class TestInitializeNestedTypes:
    """Tests for the _initialize_nested_types method of ONVIFOperator."""

    def test_initialize_nested_types_returns_instance_without_xsd_type(self):
        """Test that _initialize_nested_types returns the instance unchanged when it has
        no _xsd_type attribute."""
        operator = make_operator()
        instance = object()

        result = operator._initialize_nested_types(instance)

        assert result is instance

    def test_initialize_nested_types_does_not_replace_existing_value(self):
        """Test that _initialize_nested_types does not replace an existing value of a
        nested type attribute."""
        operator = make_operator()

        existing = object()

        class NestedType:
            """A nested type that will be initialized."""

            _xsd_type = Mock(elements=[])

        class Element:
            """An element that represents a nested type."""

            type = NestedType

        class XsdType:
            """An XSD type that has a nested type element."""

            elements = [
                ("Nested", Element()),
            ]

        class Instance:
            """An instance that has a nested type attribute."""

            _xsd_type = XsdType

            def __init__(self):
                """Init instance."""
                self.Nested = existing

        instance = Instance()

        result = operator._initialize_nested_types(instance)

        assert result is instance
        assert instance.Nested is existing

    def test_initialize_nested_types_ignores_simple_type(self):
        """Test that _initialize_nested_types does not replace a nested type attribute
        if it is a simple type."""
        operator = make_operator()

        class SimpleType:
            """A simple type that does not have nested elements."""

            pass

        class Element:
            """An element that represents a simple type."""

            type = SimpleType

        class XsdType:
            """An XSD type that has a simple type element."""

            elements = [
                ("Value", Element()),
            ]

        class Instance:
            """An instance that has a simple type attribute."""

            _xsd_type = XsdType

            def __init__(self):
                """Init instance."""
                self.Value = None

        instance = Instance()

        result = operator._initialize_nested_types(instance)

        assert result is instance
        assert instance.Value is None

    def test_initialize_nested_types_handles_xsd_processing_error(self):
        """Test that _initialize_nested_types handles an AttributeError when accessing
        elements of the XSD type."""
        operator = make_operator()

        class BrokenXsd:
            """Simulate an XSD type that raises an AttributeError when accessing
            elements."""

            @property
            def elements(self):
                """Simulate an error when accessing elements."""
                raise AttributeError("broken XSD")

        class Instance:
            """Simulate an instance with a broken _xsd_type."""

            _xsd_type = BrokenXsd()

        instance = Instance()

        result = operator._initialize_nested_types(instance)

        assert result is instance
