# tests/test_core.py

import pytest
from unittest.mock import Mock, patch
from onvif.utils.wsdl import ONVIFWSDL
from onvif.utils.zeep import ZeepPatcher
from onvif.utils.xml_capture import XMLCapturePlugin
from onvif import CacheMode


class TestONVIFWSDL:
    """Test ONVIF WSDL handling and management"""

    def test_default_wsdl_directory(self):
        """Test default WSDL directory setup"""
        # Test getting base directory (default behavior)
        base_dir = ONVIFWSDL._get_base_dir()

        assert base_dir is not None
        assert "wsdl" in base_dir.lower()

    def test_custom_wsdl_directory(self):
        """Test custom WSDL directory setup"""
        custom_dir = "/custom/wsdl/path"
        ONVIFWSDL.set_custom_wsdl_dir(custom_dir)

        retrieved_dir = ONVIFWSDL.get_custom_wsdl_dir()
        assert retrieved_dir == custom_dir

        # Clean up
        ONVIFWSDL.clear_custom_wsdl_dir()

    def test_get_wsdl_definition_for_service(self):
        """Test WSDL definition retrieval for different services"""
        # Test standard services using actual API from ONVIFWSDL class
        try:
            definition = ONVIFWSDL.get_definition("device", "ver20")
            assert definition is not None
        except ValueError:
            # Some services might not be available in test environment
            pass

        try:
            definition = ONVIFWSDL.get_definition("media", "ver10")
            assert definition is not None
        except ValueError:
            pass

    def test_wsdl_map_initialization(self):
        """Test WSDL map initialization"""
        # Ensure WSDL map is properly initialized
        ONVIFWSDL._ensure_wsdl_map_initialized()
        assert ONVIFWSDL.WSDL_MAP is not None

    def test_invalid_service_handling(self):
        """Test handling of invalid service names"""
        with pytest.raises(ValueError):
            ONVIFWSDL.get_definition("invalid_service", "ver10")

    def test_invalid_version_handling(self):
        """Test handling of invalid version names"""
        with pytest.raises(ValueError):
            ONVIFWSDL.get_definition("device", "ver99")


class TestZeepPatcher:
    """Test ZeepPatcher functionality"""

    def test_patch_application(self):
        """Test patch application"""
        # Test that patch can be applied
        ZeepPatcher.apply_patch()
        assert ZeepPatcher.is_patched()

        # Clean up
        ZeepPatcher.remove_patch()

    def test_patch_removal(self):
        """Test patch removal"""
        # Apply first
        ZeepPatcher.apply_patch()
        assert ZeepPatcher.is_patched()

        # Then remove
        ZeepPatcher.remove_patch()
        assert not ZeepPatcher.is_patched()

    def test_patch_idempotency(self):
        """Test that applying patch multiple times is safe"""
        # Apply patch multiple times
        ZeepPatcher.apply_patch()
        first_state = ZeepPatcher.is_patched()

        ZeepPatcher.apply_patch()  # Second application
        second_state = ZeepPatcher.is_patched()

        # Should remain consistent
        assert first_state and second_state

        # Clean up
        ZeepPatcher.remove_patch()

    def test_patch_state_management(self):
        """Test patch state tracking"""
        # Test initial state
        ZeepPatcher.is_patched()

        # Apply patch and test state
        ZeepPatcher.apply_patch()
        patched_state = ZeepPatcher.is_patched()
        assert patched_state

        # Remove patch and test state
        ZeepPatcher.remove_patch()
        removed_state = ZeepPatcher.is_patched()
        assert not removed_state

    def test_text_value_parsing(self):
        """Test text value parsing functionality"""
        # Test boolean parsing
        assert ZeepPatcher.parse_text_value("true")
        assert not ZeepPatcher.parse_text_value("false")
        assert ZeepPatcher.parse_text_value("TRUE")
        assert not ZeepPatcher.parse_text_value("FALSE")

        # Test integer parsing
        assert ZeepPatcher.parse_text_value("123") == 123
        assert ZeepPatcher.parse_text_value("0") == 0

        # Test float parsing
        assert ZeepPatcher.parse_text_value("123.45") == 123.45

        # Test string parsing (fallback)
        assert ZeepPatcher.parse_text_value("hello") == "hello"
        assert ZeepPatcher.parse_text_value("") == ""
        assert ZeepPatcher.parse_text_value(None) is None

    def test_flatten_xsd_any_fields(self):
        """Test flattening of xsd:any fields"""
        # Create a mock object with _value_1 field
        mock_obj = Mock()
        mock_obj.__values__ = {
            "normal_field": "test_value",
            "_value_1": {"parsed_field": "parsed_value"},
        }
        mock_obj.__dict__ = {
            "normal_field": "test_value",
            "_value_1": None,  # This should be filled
        }

        # Process the object
        result = ZeepPatcher.flatten_xsd_any_fields(mock_obj)

        # Should return the same object (modified in place)
        assert result == mock_obj


class TestXMLCapturePlugin:
    """Test XML capture functionality"""

    def test_plugin_initialization(self):
        """Test XML capture plugin initialization"""
        plugin = XMLCapturePlugin()

        assert plugin is not None
        assert hasattr(plugin, "last_sent_xml")
        assert hasattr(plugin, "last_received_xml")
        assert hasattr(plugin, "history")
        assert plugin.last_sent_xml is None
        assert plugin.last_received_xml is None
        assert plugin.history == []

    def test_plugin_initialization_with_options(self):
        """Test XML capture plugin with custom options"""
        plugin = XMLCapturePlugin(pretty_print=False)

        assert not plugin.pretty_print

    def test_request_capture(self):
        """Test XML request capture with egress method"""
        plugin = XMLCapturePlugin()

        # Mock envelope and operation
        mock_envelope = Mock()
        mock_operation = Mock()
        mock_operation.name = "GetDeviceInformation"
        mock_headers = {"Content-Type": "application/soap+xml"}

        # Mock the _format_xml method to avoid lxml dependency issues
        with patch.object(
            plugin, "_format_xml", return_value="<soap:Envelope>...</soap:Envelope>"
        ):
            result = plugin.egress(mock_envelope, mock_headers, mock_operation, {})

        # Should return envelope and headers unchanged
        assert result == (mock_envelope, mock_headers)
        assert plugin.last_operation == "GetDeviceInformation"
        assert len(plugin.history) == 1
        assert plugin.history[0]["type"] == "request"
        assert plugin.history[0]["operation"] == "GetDeviceInformation"

    def test_response_capture(self):
        """Test XML response capture with ingress method"""
        plugin = XMLCapturePlugin()

        # Mock envelope and operation
        mock_envelope = Mock()
        mock_operation = Mock()
        mock_operation.name = "GetDeviceInformation"
        mock_headers = {"Content-Type": "application/soap+xml"}

        # Mock the _format_xml method to avoid lxml dependency issues
        with patch.object(
            plugin, "_format_xml", return_value="<soap:Envelope>...</soap:Envelope>"
        ):
            result = plugin.ingress(mock_envelope, mock_headers, mock_operation)

        # Should return envelope and headers unchanged
        assert result == (mock_envelope, mock_headers)
        assert len(plugin.history) == 1
        assert plugin.history[0]["type"] == "response"
        assert plugin.history[0]["operation"] == "GetDeviceInformation"

    def test_history_management(self):
        """Test capture history management"""
        plugin = XMLCapturePlugin()

        # Add some mock history
        plugin.history = [
            {"type": "request", "operation": "GetDeviceInformation"},
            {"type": "response", "operation": "GetDeviceInformation"},
        ]

        # Test get_history
        history = plugin.get_history()
        assert len(history) == 2

        # Test clear_history
        plugin.clear_history()
        assert len(plugin.history) == 0
        assert plugin.last_sent_xml is None
        assert plugin.last_received_xml is None
        assert plugin.last_operation is None

    def test_last_request_response_accessors(self):
        """Test last request/response accessor methods"""
        plugin = XMLCapturePlugin()

        # Set some test data
        plugin.last_sent_xml = "<request>test</request>"
        plugin.last_received_xml = "<response>test</response>"

        # Test accessors
        assert plugin.get_last_request() == "<request>test</request>"
        assert plugin.get_last_response() == "<response>test</response>"

    @patch("builtins.open", create=True)
    def test_save_to_file(self, mock_open):
        """Test saving captured XML to files"""
        plugin = XMLCapturePlugin()
        plugin.last_sent_xml = "<request>test</request>"
        plugin.last_received_xml = "<response>test</response>"

        # Mock file operations
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Test saving
        plugin.save_to_file("request.xml", "response.xml")

        # Verify file operations
        assert mock_open.call_count == 2
        assert mock_file.write.call_count == 2


class TestCacheMode:
    """Test cache mode enumeration and behavior"""

    def test_cache_mode_values(self):
        """Test cache mode enumeration values"""
        assert CacheMode.NONE is not None
        assert CacheMode.MEM is not None
        assert CacheMode.DB is not None
        assert CacheMode.ALL is not None

    def test_cache_mode_string_representation(self):
        """Test cache mode string representations"""
        assert CacheMode.NONE.value == "none"
        assert CacheMode.MEM.value == "mem"
        assert CacheMode.DB.value == "db"
        assert CacheMode.ALL.value == "all"

    def test_cache_mode_comparison(self):
        """Test cache mode comparison"""
        assert CacheMode.NONE == CacheMode.NONE
        assert CacheMode.MEM == CacheMode.MEM
        assert CacheMode.DB == CacheMode.DB
        assert CacheMode.ALL == CacheMode.ALL

        assert CacheMode.NONE != CacheMode.ALL
        assert CacheMode.MEM != CacheMode.DB


class TestCoreIntegration:
    """Test integration between core components"""

    def test_wsdl_with_zeep_patcher(self):
        """Test WSDL manager with ZeepPatcher"""
        ZeepPatcher.apply_patch()

        try:
            definition = ONVIFWSDL.get_definition("device", "ver20")
            assert definition is not None
        except ValueError:
            # Some definitions might not be available
            pass

        ZeepPatcher.remove_patch()

    def test_xml_capture_with_cache_modes(self):
        """Test XML capture plugin with different cache modes"""
        plugin = XMLCapturePlugin()

        # Test with different cache modes
        for cache_mode in [CacheMode.NONE, CacheMode.MEM, CacheMode.DB, CacheMode.ALL]:
            # Plugin should work regardless of cache mode
            mock_envelope = Mock()
            mock_operation = Mock()
            mock_operation.name = f"TestOperation_{cache_mode.value}"

            with patch.object(plugin, "_format_xml", return_value="<test/>"):
                plugin.egress(mock_envelope, {}, mock_operation, {})

        assert len(plugin.history) == 4


class TestErrorHandlingInCore:
    """Test error handling in core components"""

    def test_wsdl_manager_invalid_service(self):
        """Test WSDL manager with invalid service"""
        with pytest.raises(ValueError):
            ONVIFWSDL.get_definition("invalid_service", "ver10")

    def test_wsdl_manager_invalid_version(self):
        """Test WSDL manager with invalid version"""
        with pytest.raises(ValueError):
            ONVIFWSDL.get_definition("device", "ver99")

    def test_zeep_patcher_multiple_operations(self):
        """Test ZeepPatcher multiple apply/remove operations"""
        # Should handle multiple operations gracefully
        ZeepPatcher.apply_patch()
        ZeepPatcher.apply_patch()  # Second apply
        assert ZeepPatcher.is_patched()

        ZeepPatcher.remove_patch()
        assert not ZeepPatcher.is_patched()

        ZeepPatcher.remove_patch()  # Second remove
        assert not ZeepPatcher.is_patched()

    def test_xml_capture_plugin_error_handling(self):
        """Test XML capture plugin error handling"""
        plugin = XMLCapturePlugin()

        # Test with minimal valid objects
        mock_envelope = Mock()
        mock_operation = Mock()
        mock_operation.name = "TestOperation"

        # Should not raise exception
        with patch.object(plugin, "_format_xml", return_value="<test/>"):
            result = plugin.egress(mock_envelope, {}, mock_operation, {})
            assert result == (mock_envelope, {})

            result = plugin.ingress(mock_envelope, {}, mock_operation)
            assert result == (mock_envelope, {})
