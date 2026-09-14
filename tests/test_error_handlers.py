"""Tests for ONVIF error handling utilities."""

from unittest.mock import Mock

import pytest

from onvif.utils.error_handlers import (
    ignore_unsupported,
    is_action_not_supported,
    safe_call,
)
from onvif.utils.exceptions import ONVIFOperationException

# Try to import zeep, use mock if not available
try:
    from zeep.exceptions import Fault
except ImportError:
    # Create mock Fault class for testing
    class Fault(Exception):  # type: ignore[no-redef]
        """Mock SOAP Fault."""

        def __init__(self, code=None, message=None, detail=None, subcodes=None):
            self.code = code
            self.message = message
            self.detail = detail
            self.subcodes = subcodes
            super().__init__(message or "Mock SOAP Fault")


class TestONVIFErrorHandler:
    """Test ONVIF error handler functionality."""

    def test_is_action_not_supported_with_onvif_exception(self):
        """Test ActionNotSupported detection with ONVIFOperationException."""
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        result = is_action_not_supported(onvif_exception)

        assert result

    def test_is_action_not_supported_with_fault_directly(self):
        """Test ActionNotSupported detection with Fault directly."""
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        result = is_action_not_supported(mock_fault)

        assert result

    def test_is_action_not_supported_string_fallback(self):
        """Test ActionNotSupported detection with string fallback."""
        mock_subcode = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        result = is_action_not_supported(mock_fault)

        assert result

    def test_is_action_not_supported_false_case(self):
        """Test ActionNotSupported detection returns False for other errors."""
        mock_subcode = Mock()
        mock_subcode.localname = "InvalidArgument"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        result = is_action_not_supported(onvif_exception)

        assert not result

    def test_is_action_not_supported_no_subcodes(self):
        """Test ActionNotSupported detection with no subcodes."""
        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = None

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        result = is_action_not_supported(onvif_exception)

        assert not result

    def test_is_action_not_supported_non_fault_exception(self):
        """Test ActionNotSupported detection with non-Fault exception."""
        generic_exception = ValueError("Some error")
        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, generic_exception)

        result = is_action_not_supported(onvif_exception)

        assert not result

    def test_is_action_not_supported_exception_handling(self):
        """Test ActionNotSupported detection handles exceptions gracefully."""
        mock_subcode = Mock()
        mock_subcode.localname = Mock(side_effect=Exception("Access error"))

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        result = is_action_not_supported(mock_fault)

        assert not result

    def test_safe_call_success(self):
        """Test safe_call with successful function execution."""

        def successful_function():
            return "success_result"

        result = safe_call(successful_function)

        assert result == "success_result"

    def test_safe_call_with_action_not_supported(self):
        """Test safe_call with ActionNotSupported error."""
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        def failing_function():
            raise onvif_exception

        result = safe_call(failing_function, default="default_value")

        assert result == "default_value"

    def test_safe_call_with_action_not_supported_no_default(self):
        """Test safe_call with ActionNotSupported error and no default."""
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        def failing_function():
            raise onvif_exception

        result = safe_call(failing_function)

        assert result is None

    def test_safe_call_with_other_onvif_exception(self):
        """Test safe_call with non-ActionNotSupported ONVIF exception."""
        mock_subcode = Mock()
        mock_subcode.localname = "InvalidArgument"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        def failing_function():
            raise onvif_exception

        with pytest.raises(ONVIFOperationException):
            safe_call(failing_function)

    def test_safe_call_with_generic_exception(self):
        """Test safe_call with generic exception."""

        def failing_function():
            raise ValueError("Some error")

        with pytest.raises(ValueError):
            safe_call(failing_function)

    def test_safe_call_ignore_unsupported_false(self):
        """Test safe_call with handle_unsupported=False."""
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        def failing_function():
            raise onvif_exception

        with pytest.raises(ONVIFOperationException):
            safe_call(failing_function, handle_unsupported=False)

    def test_ignore_unsupported_decorator_success(self):
        """Test ignore_unsupported decorator with successful function."""

        @ignore_unsupported
        def successful_function():
            return "success_result"

        result = successful_function()

        assert result == "success_result"

    def test_ignore_unsupported_decorator_with_action_not_supported(self):
        """Test ignore_unsupported decorator with ActionNotSupported error."""
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        @ignore_unsupported
        def failing_function():
            raise onvif_exception

        result = failing_function()

        assert result is None

    def test_ignore_unsupported_decorator_with_other_exception(self):
        """Test ignore_unsupported decorator with other exceptions."""
        mock_subcode = Mock()
        mock_subcode.localname = "InvalidArgument"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        @ignore_unsupported
        def failing_function():
            raise onvif_exception

        with pytest.raises(ONVIFOperationException):
            failing_function()

    def test_ignore_unsupported_decorator_with_args_kwargs(self):
        """Test ignore_unsupported decorator preserves function arguments."""

        @ignore_unsupported
        def function_with_params(
            arg1,
            arg2,
            kwarg1=None,
            kwarg2="default",
        ):
            return f"args: {arg1}, {arg2}, kwargs: {kwarg1}, {kwarg2}"

        result = function_with_params(
            "test1",
            "test2",
            kwarg1="kw1",
            kwarg2="kw2",
        )

        assert result == "args: test1, test2, kwargs: kw1, kw2"


class TestErrorHandlerIntegration:
    """Test error handler integration scenarios."""

    def test_multiple_subcodes_detection(self):
        """Test ActionNotSupported detection with multiple subcodes."""
        mock_subcode1 = Mock()
        mock_subcode1.localname = "InvalidArgument"

        mock_subcode2 = Mock()
        mock_subcode2.localname = "ActionNotSupported"

        mock_subcode3 = Mock()
        mock_subcode3.localname = "OutOfRange"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [
            mock_subcode1,
            mock_subcode2,
            mock_subcode3,
        ]

        result = is_action_not_supported(mock_fault)

        assert result

    def test_real_world_scenario_safe_call(self):
        """Test safe_call in real-world scenario."""
        call_count = 0

        def unreliable_onvif_operation():
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                mock_subcode = Mock()
                mock_subcode.localname = "ActionNotSupported"

                mock_fault = Mock(spec=Fault)
                mock_fault.subcodes = [mock_subcode]

                raise ONVIFOperationException(
                    "GetAnalyticsConfiguration",
                    mock_fault,
                )

            if call_count == 2:
                return {"config": "analytics_config"}

            raise ONVIFOperationException(
                "GetAnalyticsConfiguration",
                ValueError("Network error"),
            )

        result1 = safe_call(unreliable_onvif_operation)
        assert result1 is None

        result2 = safe_call(unreliable_onvif_operation)
        assert result2 == {"config": "analytics_config"}

        with pytest.raises(ONVIFOperationException):
            safe_call(unreliable_onvif_operation)

    def test_nested_error_handler_usage(self):
        """Test nested usage of error handling utilities."""

        @ignore_unsupported
        def outer_function():
            def inner_function():
                mock_subcode = Mock()
                mock_subcode.localname = "ActionNotSupported"

                mock_fault = Mock(spec=Fault)
                mock_fault.subcodes = [mock_subcode]

                raise ONVIFOperationException(
                    "InnerOperation",
                    mock_fault,
                )

            return safe_call(inner_function, default="inner_default")

        result = outer_function()

        assert result == "inner_default"
