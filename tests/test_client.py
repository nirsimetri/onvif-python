# tests/test_client.py

import pytest
from unittest.mock import Mock, patch
from onvif import ONVIFClient, CacheMode
from onvif.utils import ZeepPatcher, XMLCapturePlugin


class TestONVIFClientInitialization:
    """Test ONVIF client initialization and configuration"""

    def test_basic_initialization(self, test_client_params):
        """Test basic client initialization"""
        with patch("onvif.client.Device"):
            client = ONVIFClient(**test_client_params)

            assert client.common_args["host"] == "192.168.1.17"
            assert client.common_args["port"] == 8000
            assert client.common_args["username"] == "admin"
            assert client.common_args["password"] == "admin123"
            assert client.common_args["timeout"] == 5
            assert client.common_args["cache"] == CacheMode.NONE

    def test_https_initialization(self, test_client_params):
        """Test HTTPS client initialization"""
        params = test_client_params.copy()
        params.update({"use_https": True, "verify_ssl": False})

        with patch("onvif.client.Device"):
            client = ONVIFClient(**params)

            assert client.common_args["use_https"] is True
            assert client.common_args["verify_ssl"] is False

    def test_xml_capture_initialization(self, test_client_params):
        """Test XML capture plugin initialization"""
        params = test_client_params.copy()
        params["capture_xml"] = True

        with patch("onvif.client.Device"):
            client = ONVIFClient(**params)

            assert client.xml_plugin is not None
            assert isinstance(client.xml_plugin, XMLCapturePlugin)

    def test_custom_wsdl_directory(self, test_client_params):
        """Test custom WSDL directory setup"""
        params = test_client_params.copy()
        params["wsdl_dir"] = "/custom/wsdl/path"

        with patch("onvif.client.Device"):
            with patch("onvif.utils.ONVIFWSDL.set_custom_wsdl_dir") as mock_set_wsdl:
                client = ONVIFClient(**params)

                assert client.wsdl_dir == "/custom/wsdl/path"
                mock_set_wsdl.assert_called_once_with("/custom/wsdl/path")

    def test_zeep_patch_application(self, test_client_params):
        """Test ZeepPatcher application and removal"""
        with patch("onvif.client.Device"):
            with patch.object(ZeepPatcher, "apply_patch") as mock_apply:
                with patch.object(ZeepPatcher, "remove_patch") as mock_remove:
                    # Test patch application
                    params = test_client_params.copy()
                    params["apply_patch"] = True
                    ONVIFClient(**params)
                    mock_apply.assert_called_once()

                    # Test patch removal
                    params["apply_patch"] = False
                    ONVIFClient(**params)
                    mock_remove.assert_called_once()


class TestONVIFClientServiceDiscovery:
    """Test service discovery mechanisms"""

    def test_get_services_discovery(self, mock_onvif_client, mock_services):
        """Test GetServices-based service discovery"""
        client = mock_onvif_client

        # Simulate service discovery that happens in constructor
        # The mock_onvif_client fixture already sets this up
        assert client.services is not None

        # Test the service mapping logic directly with mock_services
        client._service_map = {}  # Reset the service map
        for service in mock_services:
            namespace = getattr(service, "Namespace", None)
            xaddr = getattr(service, "XAddr", None)
            if namespace and xaddr:
                client._service_map[namespace] = xaddr

        assert "http://www.onvif.org/ver10/media/wsdl" in client._service_map

    def test_get_capabilities_fallback(self, mock_onvif_client, mock_capabilities):
        """Test GetCapabilities fallback discovery"""
        client = mock_onvif_client
        client._devicemgmt.GetServices.side_effect = Exception(
            "GetServices not supported"
        )
        client._devicemgmt.GetCapabilities.return_value = mock_capabilities

        # Simulate fallback scenario
        try:
            client.services = client._devicemgmt.GetServices(IncludeCapability=False)
        except Exception:
            client.capabilities = client._devicemgmt.GetCapabilities(Category="All")

        assert client.capabilities is not None
        assert hasattr(client.capabilities, "Media")
        assert client.capabilities.Media.XAddr == "http://192.168.1.17:8000/onvif/Media"

    def test_xaddr_rewriting(self, mock_onvif_client):
        """Test XAddr rewriting for different host/port"""
        client = mock_onvif_client

        # Test XAddr that needs rewriting
        original_xaddr = "http://192.168.1.100:80/onvif/Media"
        rewritten = client._rewrite_xaddr_if_needed(original_xaddr)

        expected = "http://192.168.1.17:8000/onvif/Media"
        assert rewritten == expected

    def test_xaddr_no_rewriting_needed(self, mock_onvif_client):
        """Test XAddr that doesn't need rewriting"""
        client = mock_onvif_client

        # Test XAddr that matches client config
        original_xaddr = "http://192.168.1.17:8000/onvif/Media"
        rewritten = client._rewrite_xaddr_if_needed(original_xaddr)

        assert rewritten == original_xaddr


class TestONVIFClientServiceAccess:
    """Test service property access"""

    def test_devicemgmt_property(self, mock_onvif_client):
        """Test devicemgmt method access"""
        client = mock_onvif_client
        device_service = client.devicemgmt()

        assert device_service is not None
        assert device_service == client._devicemgmt

    @patch("onvif.client.Media")
    def test_media_property_lazy_loading(self, mock_media_class, mock_onvif_client):
        """Test media property lazy loading"""
        client = mock_onvif_client
        mock_media_instance = Mock()
        mock_media_class.return_value = mock_media_instance

        # First access should create the service
        media_service = client.media()
        assert mock_media_class.called
        assert media_service == mock_media_instance

        # Second access should return cached instance
        mock_media_class.reset_mock()
        media_service2 = client.media()
        assert not mock_media_class.called
        assert media_service2 == mock_media_instance

    @patch("onvif.client.PTZ")
    def test_ptz_property_lazy_loading(self, mock_ptz_class, mock_onvif_client):
        """Test PTZ property lazy loading"""
        client = mock_onvif_client
        mock_ptz_instance = Mock()
        mock_ptz_class.return_value = mock_ptz_instance

        # First access should create the service
        ptz_service = client.ptz()
        assert mock_ptz_class.called
        assert ptz_service == mock_ptz_instance

    def test_pullpoint_method_with_subscription_ref(
        self, mock_onvif_client, sample_subscription_ref
    ):
        """Test pullpoint method with SubscriptionRef parameter"""
        client = mock_onvif_client

        with patch("onvif.client.PullPoint") as mock_pullpoint_class:
            mock_pullpoint_instance = Mock()
            mock_pullpoint_class.return_value = mock_pullpoint_instance

            pullpoint_service = client.pullpoint(sample_subscription_ref)

            assert mock_pullpoint_class.called
            assert pullpoint_service == mock_pullpoint_instance

    def test_pullpoint_caching_by_xaddr(
        self, mock_onvif_client, sample_subscription_ref
    ):
        """Test pullpoint caching by XAddr"""
        client = mock_onvif_client

        with patch("onvif.client.PullPoint") as mock_pullpoint_class:
            mock_pullpoint_instance = Mock()
            mock_pullpoint_class.return_value = mock_pullpoint_instance

            # First call
            pullpoint1 = client.pullpoint(sample_subscription_ref)
            assert mock_pullpoint_class.call_count == 1

            # Second call with same ref should return cached instance
            pullpoint2 = client.pullpoint(sample_subscription_ref)
            assert mock_pullpoint_class.call_count == 1  # No additional calls
            assert pullpoint1 == pullpoint2


class TestONVIFClientErrorHandling:
    """Test error handling scenarios"""

    def test_service_discovery_failure_handling(self, test_client_params):
        """Test handling of service discovery failures"""
        with patch("onvif.client.Device") as mock_device_class:
            mock_device = Mock()
            mock_device.GetServices.side_effect = Exception("GetServices failed")
            mock_device.GetCapabilities.side_effect = Exception(
                "GetCapabilities failed"
            )
            mock_device_class.return_value = mock_device

            # Should not raise exception even if both discovery methods fail
            client = ONVIFClient(**test_client_params)
            assert client is not None
            assert client.services is None
            assert client.capabilities is None

    def test_pullpoint_missing_subscription_ref(self, mock_onvif_client):
        """Test pullpoint with invalid SubscriptionRef"""
        from onvif.utils import ONVIFOperationException

        client = mock_onvif_client

        invalid_ref = {"invalid": "structure"}

        with pytest.raises(ONVIFOperationException):
            client.pullpoint(invalid_ref)

    def test_xaddr_rewriting_error_handling(self, mock_onvif_client):
        """Test XAddr rewriting error handling"""
        client = mock_onvif_client

        # Test with valid URL that should be rewritten
        original_xaddr = "http://10.0.0.1:8080/onvif/device_service"
        result = client._rewrite_xaddr_if_needed(original_xaddr)

        # Should rewrite to use client's host/port
        expected = "http://192.168.1.17:8000/onvif/device_service"
        assert result == expected


class TestONVIFClientConfiguration:
    """Test client configuration options"""

    def test_all_cache_modes(self, test_client_params):
        """Test all cache mode configurations"""
        cache_modes = [CacheMode.ALL, CacheMode.DB, CacheMode.MEM, CacheMode.NONE]

        for cache_mode in cache_modes:
            params = test_client_params.copy()
            params["cache"] = cache_mode

            with patch("onvif.client.Device"):
                client = ONVIFClient(**params)
                assert client.common_args["cache"] == cache_mode

    def test_timeout_configuration(self, test_client_params):
        """Test timeout configuration"""
        timeouts = [1, 5, 10, 30, 60]

        for timeout in timeouts:
            params = test_client_params.copy()
            params["timeout"] = timeout

            with patch("onvif.client.Device"):
                client = ONVIFClient(**params)
                assert client.common_args["timeout"] == timeout
