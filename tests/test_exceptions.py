# tests/test_exceptions.py

import pytest
from unittest.mock import Mock

# Import from onvif main package to match actual structure
from onvif.utils.exceptions import ONVIFOperationException

# Try to import these dependencies, use mocks if not available
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

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    # Create mock requests module for testing
    class MockRequestsModule:
        class exceptions:
            class RequestException(Exception):
                pass

            class ConnectionError(RequestException):
                pass

            class Timeout(RequestException):
                pass

            class ReadTimeout(Timeout):
                pass

    requests = MockRequestsModule()
    REQUESTS_AVAILABLE = False


class TestONVIFOperationException:
    """Test ONVIFOperationException class"""

    def test_soap_fault_exception(self):
        """Test ONVIFOperationException with SOAP fault"""
        # Create a mock SOAP fault
        mock_fault = Mock(spec=Fault)
        mock_fault.code = "SOAP-ENV:Client"
        mock_fault.message = "Authentication failed"
        mock_fault.detail = None
        mock_fault.subcodes = None

        operation = "GetDeviceInformation"
        exception = ONVIFOperationException(operation, mock_fault)

        assert exception.operation == operation
        assert exception.original_exception == mock_fault
        assert "SOAP Error" in str(exception)
        assert "Authentication failed" in str(exception)
        assert operation in str(exception)

    def test_soap_fault_with_subcodes(self):
        """Test ONVIFOperationException with SOAP fault containing subcodes"""
        # Create mock objects for subcodes (simulating QName behavior)
        mock_qname1 = Mock()
        mock_qname1.localname = "ActionNotSupported"
        mock_qname2 = Mock()
        mock_qname2.localname = "InvalidParameters"

        mock_fault = Mock(spec=Fault)
        mock_fault.code = "SOAP-ENV:Server"
        mock_fault.message = "Operation failed"
        mock_fault.detail = "Additional error details"
        mock_fault.subcodes = [mock_qname1, mock_qname2]

        operation = "GetVideoEncoderConfiguration"
        exception = ONVIFOperationException(operation, mock_fault)

        error_str = str(exception)
        assert "SOAP Error" in error_str
        assert "ActionNotSupported, InvalidParameters" in error_str
        assert "Operation failed" in error_str
        assert "Additional error details" in error_str

    def test_soap_fault_with_invalid_subcodes(self):
        """Test ONVIFOperationException with invalid subcodes that cause exceptions"""
        mock_fault = Mock(spec=Fault)
        mock_fault.code = "SOAP-ENV:Client"
        mock_fault.message = "Test error"
        mock_fault.detail = None
        mock_fault.subcodes = ["invalid", "subcodes"]  # Not QName objects

        operation = "TestOperation"
        exception = ONVIFOperationException(operation, mock_fault)

        # Should handle invalid subcodes gracefully
        error_str = str(exception)
        assert "SOAP Error" in error_str
        assert "Test error" in error_str

    def test_requests_exception(self):
        """Test ONVIFOperationException with requests exception"""
        mock_requests_error = requests.exceptions.ConnectionError("Connection refused")

        operation = "GetCapabilities"
        exception = ONVIFOperationException(operation, mock_requests_error)

        assert exception.operation == operation
        assert exception.original_exception == mock_requests_error
        assert "Protocol Error" in str(exception)
        assert "Connection refused" in str(exception)
        assert operation in str(exception)

    def test_requests_timeout_exception(self):
        """Test ONVIFOperationException with requests timeout"""
        mock_timeout_error = requests.exceptions.Timeout("Request timed out")

        operation = "GetProfiles"
        exception = ONVIFOperationException(operation, mock_timeout_error)

        error_str = str(exception)
        assert "Protocol Error" in error_str
        assert "Request timed out" in error_str
        assert operation in error_str

    def test_generic_exception(self):
        """Test ONVIFOperationException with generic exception"""
        mock_generic_error = ValueError("Invalid parameter value")

        operation = "SetVideoEncoderConfiguration"
        exception = ONVIFOperationException(operation, mock_generic_error)

        assert exception.operation == operation
        assert exception.original_exception == mock_generic_error
        assert "Application Error" in str(exception)
        assert "Invalid parameter value" in str(exception)
        assert operation in str(exception)

    def test_exception_inheritance(self):
        """Test that ONVIFOperationException is properly inherited from Exception"""
        mock_error = Exception("Test error")
        operation = "TestOperation"
        exception = ONVIFOperationException(operation, mock_error)

        assert isinstance(exception, Exception)
        assert hasattr(exception, "operation")
        assert hasattr(exception, "original_exception")

    def test_soap_fault_missing_attributes(self):
        """Test SOAP fault handling when some attributes are missing"""
        mock_fault = Mock(spec=Fault)
        # Only set some attributes, leave others as None
        mock_fault.message = "Partial error info"
        mock_fault.code = None
        mock_fault.faultcode = "SOAP-ENV:Server"  # Fallback attribute
        mock_fault.detail = None
        mock_fault.subcodes = None

        operation = "GetSystemDateAndTime"
        exception = ONVIFOperationException(operation, mock_fault)

        error_str = str(exception)
        assert "SOAP Error" in error_str
        assert "SOAP-ENV:Server" in error_str
        assert "Partial error info" in error_str

    def test_soap_fault_no_message(self):
        """Test SOAP fault handling when message is None"""
        mock_fault = Mock(spec=Fault)
        mock_fault.code = "SOAP-ENV:Client"
        mock_fault.message = None
        mock_fault.detail = None
        mock_fault.subcodes = None
        mock_fault.__str__ = Mock(return_value="String representation of fault")

        operation = "GetNetworkInterfaces"
        exception = ONVIFOperationException(operation, mock_fault)

        error_str = str(exception)
        assert "SOAP Error" in error_str
        assert "String representation of fault" in error_str


class TestExceptionErrorMessages:
    """Test error message formatting and content"""

    def test_error_message_format(self):
        """Test that error messages follow expected format"""
        mock_fault = Mock(spec=Fault)
        mock_fault.code = "SOAP-ENV:Client"
        mock_fault.message = "Test message"
        mock_fault.detail = None
        mock_fault.subcodes = None

        operation = "TestOperation"
        exception = ONVIFOperationException(operation, mock_fault)

        error_str = str(exception)
        expected_parts = [
            f"ONVIF operation '{operation}' failed:",
            "SOAP Error:",
            "code=SOAP-ENV:Client",
            "msg=Test message",
        ]

        for part in expected_parts:
            assert part in error_str

    def test_different_operation_names(self):
        """Test with different ONVIF operation names"""
        operations = [
            "GetDeviceInformation",
            "GetProfiles",
            "GetVideoEncoderConfiguration",
            "ContinuousMove",
            "CreatePullPointSubscription",
        ]

        mock_error = Exception("Test error")

        for operation in operations:
            exception = ONVIFOperationException(operation, mock_error)
            assert operation in str(exception)
            assert exception.operation == operation


class TestExceptionIntegration:
    """Test exception integration with real scenarios"""

    def test_authentication_scenario(self):
        """Test exception for authentication failure scenario"""
        mock_fault = Mock(spec=Fault)
        mock_fault.code = "SOAP-ENV:Client"
        mock_fault.message = "Authentication failed"
        mock_fault.detail = "Invalid username or password"
        mock_fault.subcodes = None

        operation = "GetCapabilities"
        exception = ONVIFOperationException(operation, mock_fault)

        error_str = str(exception)
        assert "Authentication failed" in error_str
        assert "Invalid username or password" in error_str

        # Should be useful for error handling
        assert exception.original_exception == mock_fault
        assert isinstance(exception.original_exception, Fault)

    def test_network_error_scenario(self):
        """Test exception for network error scenario"""
        network_error = requests.exceptions.ConnectionError(
            "HTTPConnectionPool(host='192.168.1.17', port=8000): "
            "Max retries exceeded with url: /onvif/device_service"
        )

        operation = "GetDeviceInformation"
        exception = ONVIFOperationException(operation, network_error)

        error_str = str(exception)
        assert "Protocol Error" in error_str
        assert "192.168.1.17" in error_str
        assert "Max retries exceeded" in error_str

    def test_timeout_scenario(self):
        """Test exception for timeout scenario"""
        timeout_error = requests.exceptions.ReadTimeout(
            "HTTPSConnectionPool(host='192.168.1.17', port=443): "
            "Read timed out. (read timeout=5)"
        )

        operation = "GetStreamUri"
        exception = ONVIFOperationException(operation, timeout_error)

        error_str = str(exception)
        assert "Protocol Error" in error_str
        assert "Read timed out" in error_str
        assert "timeout=5" in error_str

    def test_service_unavailable_scenario(self):
        """Test exception for service unavailable scenario"""
        mock_fault = Mock(spec=Fault)
        mock_fault.code = "SOAP-ENV:Server"
        mock_fault.message = "Service temporarily unavailable"
        mock_fault.detail = None
        mock_fault.subcodes = None

        operation = "GetAnalyticsConfigurations"
        exception = ONVIFOperationException(operation, mock_fault)

        error_str = str(exception)
        assert "Service temporarily unavailable" in error_str
        assert "SOAP-ENV:Server" in error_str


class TestExceptionUsage:
    """Test how exceptions should be used in practice"""

    def test_exception_catching(self):
        """Test that exceptions can be caught and handled properly"""
        mock_error = Exception("Test error")
        operation = "TestOperation"

        try:
            raise ONVIFOperationException(operation, mock_error)
        except ONVIFOperationException as e:
            assert e.operation == operation
            assert e.original_exception == mock_error
        except Exception:
            pytest.fail("Should catch ONVIFOperationException specifically")

    def test_exception_reraising(self):
        """Test that exceptions can be re-raised with additional context"""
        original_error = ValueError("Original error")
        operation = "FirstOperation"

        first_exception = ONVIFOperationException(operation, original_error)

        # Simulate re-raising with additional context
        try:
            raise first_exception
        except ONVIFOperationException as e:
            # Could wrap in another exception if needed
            second_operation = "SecondOperation"
            second_exception = ONVIFOperationException(second_operation, e)

            assert second_exception.operation == second_operation
            assert isinstance(
                second_exception.original_exception, ONVIFOperationException
            )
            assert second_exception.original_exception.operation == operation
