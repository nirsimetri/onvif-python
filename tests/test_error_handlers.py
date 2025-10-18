# tests/test_error_handlers.py

import pytest
from unittest.mock import Mock
from onvif.utils.error_handlers import ONVIFErrorHandler
from onvif.utils.exceptions import ONVIFOperationException

# Try to import zeep, use mock if not available
try:
    from zeep.exceptions import Fault

    ZEEP_AVAILABLE = True
except ImportError:
    # Create mock Fault class for testing
    class Fault(Exception):
        def __init__(self, code=None, message=None, detail=None, subcodes=None):
            self.code = code
            self.message = message
            self.detail = detail
            self.subcodes = subcodes
            super().__init__(message or "Mock SOAP Fault")

    ZEEP_AVAILABLE = False


class TestONVIFErrorHandler:
    """Test ONVIF error handler functionality"""

    def test_is_action_not_supported_with_onvif_exception(self):
        """Test ActionNotSupported detection with ONVIFOperationException"""
        # Create mock subcode with ActionNotSupported
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        result = ONVIFErrorHandler.is_action_not_supported(onvif_exception)
        assert result

    def test_is_action_not_supported_with_fault_directly(self):
        """Test ActionNotSupported detection with Fault directly"""
        # Create mock subcode with ActionNotSupported
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        result = ONVIFErrorHandler.is_action_not_supported(mock_fault)
        assert result

    def test_is_action_not_supported_string_fallback(self):
        """Test ActionNotSupported detection with string fallback"""
        # Create mock subcode without localname but string contains ActionNotSupported
        mock_subcode = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        result = ONVIFErrorHandler.is_action_not_supported(mock_fault)
        assert result

    def test_is_action_not_supported_false_case(self):
        """Test ActionNotSupported detection returns False for other errors"""
        # Create mock subcode with different error
        mock_subcode = Mock()
        mock_subcode.localname = "InvalidArgument"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        result = ONVIFErrorHandler.is_action_not_supported(onvif_exception)
        assert not result

    def test_is_action_not_supported_no_subcodes(self):
        """Test ActionNotSupported detection with no subcodes"""
        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = None

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        result = ONVIFErrorHandler.is_action_not_supported(onvif_exception)
        assert not result

    def test_is_action_not_supported_non_fault_exception(self):
        """Test ActionNotSupported detection with non-Fault exception"""
        generic_exception = ValueError("Some error")
        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, generic_exception)

        result = ONVIFErrorHandler.is_action_not_supported(onvif_exception)
        assert not result

    def test_is_action_not_supported_exception_handling(self):
        """Test ActionNotSupported detection handles exceptions gracefully"""
        # Create a faulty mock that raises exception when accessing localname
        mock_subcode = Mock()
        mock_subcode.localname = Mock(side_effect=Exception("Access error"))

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        # Should not raise exception, should return False
        result = ONVIFErrorHandler.is_action_not_supported(mock_fault)
        assert not result

    def test_safe_call_success(self):
        """Test safe_call with successful function execution"""

        def successful_function():
            return "success_result"

        result = ONVIFErrorHandler.safe_call(successful_function)
        assert result == "success_result"

    def test_safe_call_with_action_not_supported(self):
        """Test safe_call with ActionNotSupported error"""
        # Create ActionNotSupported error
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        def failing_function():
            raise onvif_exception

        # Should return default value instead of raising
        result = ONVIFErrorHandler.safe_call(failing_function, default="default_value")
        assert result == "default_value"

    def test_safe_call_with_action_not_supported_no_default(self):
        """Test safe_call with ActionNotSupported error and no default"""
        # Create ActionNotSupported error
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        def failing_function():
            raise onvif_exception

        # Should return None (default default value)
        result = ONVIFErrorHandler.safe_call(failing_function)
        assert result is None

    def test_safe_call_with_other_onvif_exception(self):
        """Test safe_call with non-ActionNotSupported ONVIF exception"""
        # Create different error
        mock_subcode = Mock()
        mock_subcode.localname = "InvalidArgument"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        def failing_function():
            raise onvif_exception

        # Should re-raise the exception
        with pytest.raises(ONVIFOperationException):
            ONVIFErrorHandler.safe_call(failing_function)

    def test_safe_call_with_generic_exception(self):
        """Test safe_call with generic exception"""

        def failing_function():
            raise ValueError("Some error")

        # Should re-raise the exception
        with pytest.raises(ValueError):
            ONVIFErrorHandler.safe_call(failing_function)

    def test_safe_call_ignore_unsupported_false(self):
        """Test safe_call with ignore_unsupported=False"""
        # Create ActionNotSupported error
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        def failing_function():
            raise onvif_exception

        # Should re-raise even ActionNotSupported when ignore_unsupported=False
        with pytest.raises(ONVIFOperationException):
            ONVIFErrorHandler.safe_call(failing_function, ignore_unsupported=False)

    def test_ignore_unsupported_decorator_success(self):
        """Test ignore_unsupported decorator with successful function"""

        @ONVIFErrorHandler.ignore_unsupported
        def successful_function():
            return "success_result"

        result = successful_function()
        assert result == "success_result"

    def test_ignore_unsupported_decorator_with_action_not_supported(self):
        """Test ignore_unsupported decorator with ActionNotSupported error"""
        # Create ActionNotSupported error
        mock_subcode = Mock()
        mock_subcode.localname = "ActionNotSupported"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        @ONVIFErrorHandler.ignore_unsupported
        def failing_function():
            raise onvif_exception

        # Should return None instead of raising
        result = failing_function()
        assert result is None

    def test_ignore_unsupported_decorator_with_other_exception(self):
        """Test ignore_unsupported decorator with other exceptions"""
        # Create different error
        mock_subcode = Mock()
        mock_subcode.localname = "InvalidArgument"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode]

        operation = "GetVideoEncoderConfiguration"
        onvif_exception = ONVIFOperationException(operation, mock_fault)

        @ONVIFErrorHandler.ignore_unsupported
        def failing_function():
            raise onvif_exception

        # Should re-raise the exception
        with pytest.raises(ONVIFOperationException):
            failing_function()

    def test_ignore_unsupported_decorator_with_args_kwargs(self):
        """Test ignore_unsupported decorator preserves function signature"""

        @ONVIFErrorHandler.ignore_unsupported
        def function_with_params(arg1, arg2, kwarg1=None, kwarg2="default"):
            return f"args: {arg1}, {arg2}, kwargs: {kwarg1}, {kwarg2}"

        result = function_with_params("test1", "test2", kwarg1="kw1", kwarg2="kw2")
        assert result == "args: test1, test2, kwargs: kw1, kw2"


class TestErrorHandlerIntegration:
    """Test error handler integration scenarios"""

    def test_multiple_subcodes_detection(self):
        """Test ActionNotSupported detection with multiple subcodes"""
        # Create multiple subcodes, one of which is ActionNotSupported
        mock_subcode1 = Mock()
        mock_subcode1.localname = "InvalidArgument"

        mock_subcode2 = Mock()
        mock_subcode2.localname = "ActionNotSupported"

        mock_subcode3 = Mock()
        mock_subcode3.localname = "OutOfRange"

        mock_fault = Mock(spec=Fault)
        mock_fault.subcodes = [mock_subcode1, mock_subcode2, mock_subcode3]

        result = ONVIFErrorHandler.is_action_not_supported(mock_fault)
        assert result

    def test_real_world_scenario_safe_call(self):
        """Test safe_call in real-world scenario"""
        call_count = 0

        def unreliable_onvif_operation():
            nonlocal call_count
            call_count += 1

            if call_count == 1:
                # First call: ActionNotSupported
                mock_subcode = Mock()
                mock_subcode.localname = "ActionNotSupported"
                mock_fault = Mock(spec=Fault)
                mock_fault.subcodes = [mock_subcode]
                raise ONVIFOperationException("GetAnalyticsConfiguration", mock_fault)
            elif call_count == 2:
                # Second call: Success
                return {"config": "analytics_config"}
            else:
                # Third call: Different error
                raise ONVIFOperationException(
                    "GetAnalyticsConfiguration", ValueError("Network error")
                )

        # First call should return None (ActionNotSupported)
        result1 = ONVIFErrorHandler.safe_call(unreliable_onvif_operation)
        assert result1 is None

        # Second call should return actual result
        result2 = ONVIFErrorHandler.safe_call(unreliable_onvif_operation)
        assert result2 == {"config": "analytics_config"}

        # Third call should raise exception (not ActionNotSupported)
        with pytest.raises(ONVIFOperationException):
            ONVIFErrorHandler.safe_call(unreliable_onvif_operation)

    def test_nested_error_handler_usage(self):
        """Test nested usage of error handlers"""

        @ONVIFErrorHandler.ignore_unsupported
        def outer_function():
            def inner_function():
                # Create ActionNotSupported error
                mock_subcode = Mock()
                mock_subcode.localname = "ActionNotSupported"
                mock_fault = Mock(spec=Fault)
                mock_fault.subcodes = [mock_subcode]
                raise ONVIFOperationException("InnerOperation", mock_fault)

            return ONVIFErrorHandler.safe_call(inner_function, default="inner_default")

        result = outer_function()
        assert result == "inner_default"
