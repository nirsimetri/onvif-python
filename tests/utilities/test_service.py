"""Tests for ONVIFService."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from onvif.utils.exceptions import ONVIFOperationException
from onvif.utils.service import ONVIFService, _is_zeep_object


class TestService(ONVIFService):
    """Concrete test implementation of ONVIFService."""

    def GetDeviceInformation(self, token=None):
        """Get device information."""
        return {"token": token}

    def GetProfiles(self, profile=None, timeout=10):
        """Get profiles."""
        return {
            "profile": profile,
            "timeout": timeout,
        }

    def SetHostname(self, name):
        """Set hostname."""
        return name

    def regular_method(self, value):
        """Regular non-ONVIF method."""
        return value

    def _private_method(self):
        """Private method."""
        return "private"


# pylint: disable=unnecessary-pass
class DescriptionService(ONVIFService):
    """Concrete test implementation of ONVIFService with method documentation."""

    def GetProfiles(self, profile, timeout=10):
        """Get profiles."""
        pass

    def SetHostname(self, name):
        """Set hostname."""
        pass


# pylint: disable=attribute-defined-outside-init
@pytest.fixture
def service():
    """Fixture that returns a TestService instance with a mocked operator."""
    test_service = object.__new__(TestService)
    test_service.operator = Mock()
    test_service.operator.service_name = "Device"
    return test_service


# pylint: disable=attribute-defined-outside-init
@pytest.fixture
def description_service():
    """Fixture that returns a DescriptionService instance with a mocked operator."""
    test_service = object.__new__(DescriptionService)
    test_service.operator = Mock(service_name="Device")
    return test_service


# pylint: disable=protected-access
class TestIsZeepObject:
    """Tests for the _is_zeep_object()."""

    @pytest.mark.parametrize(
        "obj",
        [
            None,
            object(),
            {"_xsd_type": object()},
        ],
    )
    def test_is_zeep_object_false(self, obj):
        """Test that _is_zeep_object returns False for non-Zeep objects."""
        assert _is_zeep_object(obj) is False

    def test_is_zeep_object_true(self):
        """Test that _is_zeep_object returns True for Zeep objects."""
        obj = Mock()
        obj._xsd_type = Mock()

        assert _is_zeep_object(obj) is True


# pylint: disable=redefined-outer-name,protected-access,attribute-defined-outside-init
class TestGetAttribute:
    """Tests for the __getattribute__ method of ONVIFService."""

    def test_getattribute_returns_non_callable_attribute_directly(self, service):
        """Test that __getattribute__ returns non-callable attributes directly."""
        service.value = 123

        assert service.value == 123

    def test_getattribute_does_not_wrap_private_method(self, service):
        """Test that __getattribute__ does not wrap private methods."""
        method = service._private_method

        assert method() == "private"

    def test_getattribute_does_not_wrap_operator(self, service):
        """Test that __getattribute__ does not wrap the operator attribute."""
        operator = service.operator

        assert operator is service.operator

    def test_getattribute_does_not_wrap_lowercase_method(self, service):
        """Test that __getattribute__ does not wrap lowercase methods."""
        method = service.regular_method

        assert method("test") == "test"

    def test_getattribute_wraps_uppercase_method(self, service):
        """Test that __getattribute__ wraps uppercase methods."""
        method = service.GetDeviceInformation

        assert callable(method)
        assert method() == {"token": None}

    def test_getattribute_preserves_method_arguments(self, service):
        """Test that __getattribute__ preserves method arguments."""
        result = service.GetProfiles(
            "profile-1",
            timeout=30,
        )

        assert result == {
            "profile": "profile-1",
            "timeout": 30,
        }

    def test_uppercase_method_exception_is_wrapped(self, service):
        """Test that exceptions raised by uppercase methods are wrapped in
        ONVIFOperationException."""

        def failing_method():
            raise ValueError("boom")

        service.GetDeviceInformation = failing_method

        with pytest.raises(ONVIFOperationException) as exc_info:
            service.GetDeviceInformation()

        assert exc_info.value.__cause__ is not None
        assert isinstance(exc_info.value.__cause__, ValueError)

    def test_uppercase_method_preserves_onvif_operation_exception(self, service):
        """Test that ONVIFOperationException raised by uppercase methods is
        preserved."""
        error = ONVIFOperationException(
            "GetDeviceInformation",
            RuntimeError("already wrapped"),
        )

        def failing_method():
            raise error

        service.GetDeviceInformation = failing_method

        with pytest.raises(ONVIFOperationException) as exc_info:
            service.GetDeviceInformation()

        assert exc_info.value is error

    def test_uppercase_method_uses_unknown_service_name_when_missing(self):
        """Test that ONVIFOperationException uses "Unknown" service name when operator
        has no name."""
        service = object.__new__(TestService)
        service.operator = Mock(spec=[])

        def failing_method():
            raise RuntimeError("boom")

        service.GetDeviceInformation = failing_method

        with pytest.raises(ONVIFOperationException):
            service.GetDeviceInformation()

    def test_uppercase_method_logs_service_and_method_on_failure(
        self,
        service,
        caplog,
    ):
        """Test that ONVIFOperationException logs service and method name on failure."""

        def failing_method():
            """Failing method for testing."""
            raise RuntimeError("boom")

        service.GetDeviceInformation = failing_method

        with caplog.at_level("ERROR"):
            with pytest.raises(ONVIFOperationException):
                service.GetDeviceInformation()

        assert "Device.GetDeviceInformation" in caplog.text
        assert "boom" in caplog.text


# pylint: disable=protected-access
class TestZeepObjectConversion:
    """Tests for the Zeep object conversion."""

    def test_uppercase_method_converts_zeep_object_to_kwargs(self, service):
        """Test that uppercase methods convert Zeep objects to keyword arguments."""
        params = Mock()
        params._xsd_type.elements = [
            ("ProfileToken", Mock()),
            ("Timeout", Mock()),
        ]
        params.ProfileToken = "profile-1"
        params.Timeout = 30

        mock_method = Mock(return_value="result")
        service.GetProfiles = mock_method

        with patch(
            "onvif.utils.service._is_zeep_object",
            return_value=True,
        ):
            result = service.GetProfiles(params)

        assert result == "result"

        mock_method.assert_called_once_with(
            ProfileToken="profile-1",
            Timeout=30,
        )

    def test_zeep_object_conversion_uses_all_xsd_elements(self, service):
        """Test that Zeep object conversion uses all elements defined in _xsd_type."""
        params = Mock()
        params._xsd_type.elements = [
            ("First", Mock()),
            ("Second", Mock()),
            ("Third", Mock()),
        ]
        params.First = 1
        params.Second = "two"
        params.Third = True

        mock_method = Mock(return_value="ok")
        service.SetHostname = mock_method

        with patch(
            "onvif.utils.service._is_zeep_object",
            return_value=True,
        ):
            result = service.SetHostname(params)

        assert result == "ok"

        mock_method.assert_called_once_with(
            First=1,
            Second="two",
            Third=True,
        )

    def test_zeep_object_without_elements_is_passed_normally(self, service):
        """Test that Zeep objects without _xsd_type.elements are passed as-is."""
        params = Mock()
        params._xsd_type = Mock(spec=[])

        mock_method = Mock(return_value="ok")
        service.SetHostname = mock_method

        with patch(
            "onvif.utils.service._is_zeep_object",
            return_value=True,
        ):
            result = service.SetHostname(params)

        assert result == "ok"

        mock_method.assert_called_once_with(params)

    def test_zeep_object_attribute_error_is_wrapped(self, service):
        """Test that AttributeError raised during Zeep object conversion is wrapped in
        ONVIFOperationException."""

        class Params:
            """Mock Zeep object with _xsd_type.elements that raises AttributeError."""

            _xsd_type = SimpleNamespace(elements=[("Missing", object())])

            @property
            def Missing(self):
                """Mock property that raises AttributeError to simulate missing
                attribute."""
                raise AttributeError("missing")

        params = Params()

        mock_method = Mock(return_value="ok")
        service.SetHostname = mock_method

        with patch(
            "onvif.utils.service._is_zeep_object",
            return_value=True,
        ):
            with pytest.raises(ONVIFOperationException) as exc_info:
                service.SetHostname(params)

        assert exc_info.value
        mock_method.assert_not_called()


# pylint: disable=attribute-defined-outside-init
class TestType:
    """Tests for the type() method of ONVIFService."""

    def test_type_returns_created_type(self, service):
        """Test that type() returns the created type from the operator."""
        created_type = Mock()
        service.operator.create_type.return_value = created_type

        result = service.type("SetHostname")

        assert result is created_type
        service.operator.create_type.assert_called_once_with(
            "SetHostname",
        )

    def test_type_wraps_exception(self, service):
        """Test that exceptions raised by operator.create_type are wrapped in
        ONVIFOperationException."""
        service.operator.create_type.side_effect = RuntimeError("creation failed")

        with pytest.raises(ONVIFOperationException) as exc_info:
            service.type("SetHostname")

        assert isinstance(exc_info.value.__cause__, RuntimeError)
        service.operator.create_type.assert_called_once_with(
            "SetHostname",
        )

    def test_type_wraps_exception_with_operation_name(self, service):
        """Test that ONVIFOperationException raised by operator.create_type includes
        operation name."""
        service.operator.create_type.side_effect = ValueError("invalid type")

        with pytest.raises(ONVIFOperationException) as exc_info:
            service.type("SetHostname")

        assert "type(SetHostname)" in str(exc_info.value)


# pylint: disable=attribute-defined-outside-init
class TestOperations:
    """Tests for the operations() method of ONVIFService."""

    def test_operations_returns_uppercase_callable_methods(self, service):
        """Test that operations() returns a list of uppercase callable methods."""
        operations = service.operations()

        assert operations == [
            "GetDeviceInformation",
            "GetProfiles",
            "SetHostname",
        ]

    def test_operations_returns_sorted_methods(self, service):
        """Test that operations() returns methods sorted alphabetically."""
        operations = service.operations()

        assert operations == sorted(operations)

    def test_operations_excludes_internal_methods(self, service):
        """Test that operations() excludes internal methods like private methods and
        attributes."""
        operations = service.operations()

        assert "regular_method" not in operations
        assert "_private_method" not in operations
        assert "type" not in operations
        assert "desc" not in operations
        assert "operations" not in operations

    def test_operations_handles_exception(self, service):
        """Test that operations() handles exceptions raised by dir() and returns an
        empty list."""
        with patch(
            "onvif.utils.service.dir",
            side_effect=RuntimeError("failed"),
        ):
            result = service.operations()

            assert result == []

    def test_operations_handles_operator_without_service_name(self):
        """Test that operations() works even when the operator has no service_name
        attribute."""
        service = object.__new__(TestService)
        service.operator = Mock(spec=[])

        assert service.operations() == [
            "GetDeviceInformation",
            "GetProfiles",
            "SetHostname",
        ]


# pylint: disable=attribute-defined-outside-init
class TestDesc:
    """Tests for the desc() method of ONVIFService."""

    def test_desc_returns_method_metadata(self, service):
        """Test that desc() returns method metadata including documentation, required
        and optional parameters."""
        with patch(
            "onvif.utils.service.get_method_documentation",
            return_value={"doc": "Get device information."},
        ):
            result = service.desc("GetDeviceInformation")

        assert result == {
            "doc": "Get device information.",
            "required": [],
            "optional": ["token"],
            "method_name": "GetDeviceInformation",
            "service_name": "Device",
        }

    def test_desc_extracts_required_and_optional_parameters(
        self,
        description_service,
    ):
        """Test that desc() correctly extracts required and optional parameters from
        method signature."""
        with patch(
            "onvif.utils.service.get_method_documentation",
            return_value={"doc": "Get profiles."},
        ):
            result = description_service.desc("GetProfiles")

        assert result["required"] == ["profile"]
        assert result["optional"] == ["timeout"]
        assert result["method_name"] == "GetProfiles"
        assert result["service_name"] == "Device"
        assert result["doc"] == "Get profiles."

    def test_desc_excludes_self_from_parameters(self, service):
        """Test that desc() excludes 'self' from required parameters."""
        with patch(
            "onvif.utils.service.get_method_documentation",
            return_value={"doc": "Set hostname."},
        ):
            result = service.desc("SetHostname")

        assert result["required"] == ["name"]
        assert "self" not in result["required"]

    def test_desc_returns_none_for_default_documentation(self, service):
        """Test that desc() returns None for doc when the documentation is a default
        placeholder."""
        with patch(
            "onvif.utils.service.get_method_documentation",
            return_value={
                "doc": "No description available",
            },
        ):
            result = service.desc("SetHostname")

        assert result["doc"] is None

    @pytest.mark.parametrize(
        "doc",
        [
            "No description available",
            "No documentation available",
        ],
    )
    def test_desc_filters_default_documentation(self, service, doc):
        """Test that desc() filters out default documentation and returns None for
        doc."""
        with patch(
            "onvif.utils.service.get_method_documentation",
            return_value={"doc": doc},
        ):
            result = service.desc("SetHostname")

        assert result["doc"] is None

    def test_desc_accepts_missing_documentation(self, service):
        """Test that desc() handles missing documentation gracefully and returns None
        for doc."""
        with patch(
            "onvif.utils.service.get_method_documentation",
            return_value=None,
        ):
            result = service.desc("SetHostname")

        assert result["doc"] is None

    @pytest.mark.parametrize(
        "exception",
        [
            OSError("documentation unavailable"),
            ValueError("invalid documentation"),
            AttributeError("missing documentation"),
        ],
    )
    def test_desc_documentation_failure_is_non_fatal(
        self,
        service,
        exception,
    ):
        """Test that desc() handles documentation retrieval failures gracefully and
        returns None for doc."""
        with patch(
            "onvif.utils.service.get_method_documentation",
            side_effect=exception,
        ):
            result = service.desc("SetHostname")

        assert result["doc"] is None
        assert result["required"] == ["name"]

    def test_desc_parameter_inspection_failure_is_non_fatal(self, service):
        """Test that desc() handles parameter inspection failures gracefully and returns
        empty required/optional lists."""
        with (
            patch(
                "onvif.utils.service.inspect.signature",
                side_effect=ValueError("cannot inspect"),
            ),
            patch(
                "onvif.utils.service.get_method_documentation",
                return_value={"doc": "Set hostname."},
            ),
        ):
            result = service.desc("SetHostname")

        assert result["required"] == []
        assert result["optional"] == []
        assert result["doc"] == "Set hostname."

    def test_desc_unknown_method_raises_onvif_operation_exception(self, service):
        """Test that desc() raises ONVIFOperationException for unknown methods."""
        with pytest.raises(ONVIFOperationException) as exc_info:
            service.desc("DoesNotExist")

        assert isinstance(exc_info.value.__cause__, ValueError)
        assert "DoesNotExist" in str(exc_info.value.__cause__)

    def test_desc_unknown_method_includes_available_methods(self, service):
        """Test that desc() includes available methods in the exception message for
        unknown methods."""
        with pytest.raises(ONVIFOperationException) as exc_info:
            service.desc("DoesNotExist")

        cause = exc_info.value.__cause__

        assert cause is not None
        assert "GetDeviceInformation" in str(cause)
        assert "GetProfiles" in str(cause)

    def test_desc_truncates_long_available_method_list(self):
        """Test that desc() truncates long available method lists in the exception
        message."""

        class ManyMethods(ONVIFService):
            """Concrete test implementation of ONVIFService with many methods."""

            def Alpha(self):
                """Method Alpha."""
                pass

            def Bravo(self):
                """Method Bravo."""
                pass

            def Charlie(self):
                """Method Charlie."""
                pass

            def Delta(self):
                """Method Delta."""
                pass

            def Echo(self):
                """Method Echo."""
                pass

            def Foxtrot(self):
                """Method Foxtrot."""
                pass

            def Golf(self):
                """Method Golf."""
                pass

        service = object.__new__(ManyMethods)
        service.operator = Mock(service_name="Device")

        with pytest.raises(ONVIFOperationException) as exc_info:
            service.desc("Missing")

        cause = exc_info.value.__cause__

        assert cause is not None
        assert "..." in str(cause)

    def test_desc_uses_unknown_service_name_when_operator_has_no_name(self):
        """Test that desc() uses "Unknown" service name when operator has no
        service_name attribute."""
        service = object.__new__(TestService)
        service.operator = Mock(spec=[])

        with patch(
            "onvif.utils.service.get_method_documentation",
            return_value={"doc": "Get information."},
        ):
            result = service.desc("GetDeviceInformation")

        assert result["service_name"] == "Unknown"


class TestToDict:
    """Tests for the to_dict() method of ONVIFService."""

    def test_to_dict_returns_empty_dict_for_none(self, service):
        """Test that to_dict() returns an empty dictionary when given None."""
        assert service.to_dict(None) == {}

    def test_to_dict_serializes_zeep_object(self, service):
        """Test that to_dict() serializes a Zeep object using serialize_object."""
        zeep_object = Mock()
        serialized = {
            "Name": "Camera",
            "Enabled": True,
        }

        with patch(
            "onvif.utils.service.zeep.helpers.serialize_object",
            return_value=serialized,
        ) as serialize:
            result = service.to_dict(zeep_object)

        assert result == serialized
        serialize.assert_called_once_with(zeep_object)

    def test_to_dict_returns_empty_dict_on_serialization_error(self, service):
        """Test that to_dict() returns an empty dictionary when serialization fails."""
        zeep_object = Mock()

        with patch(
            "onvif.utils.service.zeep.helpers.serialize_object",
            side_effect=ValueError("serialization failed"),
        ):
            assert service.to_dict(zeep_object) == {}

    def test_to_dict_handles_nested_serialized_object(self, service):
        """Test that to_dict() correctly handles nested serialized objects."""
        zeep_object = Mock()
        serialized = {
            "Profile": {
                "Name": "Main",
                "VideoSource": {
                    "Token": "video-1",
                },
            }
        }

        with patch(
            "onvif.utils.service.zeep.helpers.serialize_object",
            return_value=serialized,
        ):
            assert service.to_dict(zeep_object) == serialized
