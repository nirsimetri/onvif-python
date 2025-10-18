# tests/conftest.py

import pytest
from unittest.mock import Mock, patch
from onvif import ONVIFClient, CacheMode


@pytest.fixture
def mock_device_response():
    """Mock device information response"""
    mock_device = Mock()
    mock_device.Manufacturer = "Test Manufacturer"
    mock_device.Model = "Test Model"
    mock_device.FirmwareVersion = "1.0.0"
    mock_device.SerialNumber = "TEST123456"
    mock_device.HardwareId = "TEST_HW_001"
    return mock_device


@pytest.fixture
def mock_capabilities():
    """Mock capabilities response"""
    mock_caps = Mock()

    # Media capabilities
    mock_caps.Media = Mock()
    mock_caps.Media.XAddr = "http://192.168.1.17:8000/onvif/Media"

    # PTZ capabilities
    mock_caps.PTZ = Mock()
    mock_caps.PTZ.XAddr = "http://192.168.1.17:8000/onvif/PTZ"

    # Extension capabilities
    mock_caps.Extension = Mock()
    mock_caps.Extension.DeviceIO = Mock()
    mock_caps.Extension.DeviceIO.XAddr = "http://192.168.1.17:8000/onvif/DeviceIO"

    return mock_caps


@pytest.fixture
def mock_services():
    """Mock GetServices response"""
    service1 = Mock()
    service1.Namespace = "http://www.onvif.org/ver10/media/wsdl"
    service1.XAddr = "http://192.168.1.17:8000/onvif/Media"

    service2 = Mock()
    service2.Namespace = "http://www.onvif.org/ver20/ptz/wsdl"
    service2.XAddr = "http://192.168.1.17:8000/onvif/PTZ"

    return [service1, service2]


@pytest.fixture
def mock_onvif_client():
    """Create a mocked ONVIF client for testing"""
    with patch("onvif.client.Device") as mock_device_class:
        # Mock the Device class to avoid real network calls
        mock_device = Mock()
        mock_device_class.return_value = mock_device

        client = ONVIFClient(
            host="192.168.1.17",
            port=8000,
            username="admin",
            password="admin123",
            timeout=5,
            cache=CacheMode.NONE,  # Disable caching for tests
        )

        # Set up mock responses
        mock_device.GetDeviceInformation.return_value = Mock(
            Manufacturer="Test Manufacturer",
            Model="Test Model",
            FirmwareVersion="1.0.0",
            SerialNumber="TEST123456",
            HardwareId="TEST_HW_001",
        )

        # Create mock capabilities
        mock_caps = Mock()
        mock_caps.Media = Mock()
        mock_caps.Media.XAddr = "http://192.168.1.17:8000/onvif/Media"
        mock_caps.PTZ = Mock()
        mock_caps.PTZ.XAddr = "http://192.168.1.17:8000/onvif/PTZ"
        mock_caps.Extension = Mock()
        mock_caps.Extension.DeviceIO = Mock()
        mock_caps.Extension.DeviceIO.XAddr = "http://192.168.1.17:8000/onvif/DeviceIO"
        mock_device.GetCapabilities.return_value = mock_caps

        # Create mock services
        service1 = Mock()
        service1.Namespace = "http://www.onvif.org/ver10/media/wsdl"
        service1.XAddr = "http://192.168.1.17:8000/onvif/Media"
        service2 = Mock()
        service2.Namespace = "http://www.onvif.org/ver20/ptz/wsdl"
        service2.XAddr = "http://192.168.1.17:8000/onvif/PTZ"
        mock_device.GetServices.return_value = [service1, service2]

        client._devicemgmt = mock_device
        yield client


@pytest.fixture
def sample_subscription_ref():
    """Sample subscription reference for pullpoint tests"""
    return {
        "SubscriptionReference": {
            "Address": {"_value_1": "http://192.168.1.17:8000/onvif/Subscription/12345"}
        }
    }


@pytest.fixture
def test_client_params():
    """Standard test client parameters"""
    return {
        "host": "192.168.1.17",
        "port": 8000,
        "username": "admin",
        "password": "admin123",
        "timeout": 5,
        "cache": CacheMode.NONE,
    }
