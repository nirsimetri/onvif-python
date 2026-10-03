"""Integration tests for ONVIF core components."""

from unittest.mock import Mock, patch

import pytest

from onvif import CacheMode
from onvif.operator import ONVIFOperator
from onvif.utils.plugins import XMLCapturePlugin
from onvif.utils.wsdl import ONVIFWSDL
from onvif.utils.zeep import ZeepPatcher


class TestCoreIntegration:
    """Test integration between core ONVIF components."""

    def test_wsdl_definition_can_be_loaded(self):
        """Test that the WSDL definition can be loaded for a valid service."""
        definition = ONVIFWSDL.get_definition("devicemgmt")

        assert definition["path"]
        assert definition["namespace"]
        assert definition["binding"]

    def test_wsdl_definition_works_with_zeep_patcher(self):
        """Test that the WSDL definition can be loaded with ZeepPatcher applied."""
        was_patched = ZeepPatcher.is_patched()

        try:
            ZeepPatcher.apply_patch()

            definition = ONVIFWSDL.get_definition("devicemgmt")

            assert definition["path"]
            assert definition["namespace"]
            assert definition["binding"]
        finally:
            if not was_patched:
                ZeepPatcher.remove_patch()

    def test_xml_capture_plugin_can_capture_soap_exchange(self):
        """Test that the XMLCapturePlugin can capture SOAP requests and responses."""
        plugin = XMLCapturePlugin()

        envelope = Mock()
        operation = Mock()
        operation.name = "GetDeviceInformation"
        headers = {"Content-Type": "application/soap+xml"}

        with patch.object(
            plugin,
            "_format_xml",
            return_value="<soap:Envelope/>",
        ):
            assert plugin.egress(
                envelope,
                headers,
                operation,
                {},
            ) == (envelope, headers)

            assert plugin.ingress(
                envelope,
                headers,
                operation,
            ) == (envelope, headers)

        assert len(plugin.history) == 2
        assert [entry["type"] for entry in plugin.history] == [
            "request",
            "response",
        ]
        assert all(
            entry["operation"] == "GetDeviceInformation" for entry in plugin.history
        )

    def test_xml_capture_plugin_can_be_reset(self):
        """Test that the XMLCapturePlugin can be reset to its initial state."""
        plugin = XMLCapturePlugin()

        plugin.last_sent_xml = "<request/>"
        plugin.last_received_xml = "<response/>"
        plugin.last_operation = "GetDeviceInformation"
        plugin.history.append({"type": "request"})

        plugin.clear_history()

        assert not plugin.history
        assert plugin.last_sent_xml is None
        assert plugin.last_received_xml is None
        assert plugin.last_operation is None


# pylint: disable=too-few-public-methods
class TestCoreErrorHandling:
    """Test errors crossing core component boundaries."""

    @pytest.mark.parametrize(
        ("service", "version"),
        [
            ("invalid_service", "ver10"),
            ("devicemgmt", "ver99"),
        ],
    )
    def test_invalid_wsdl_definition_is_rejected(
        self,
        service,
        version,
    ):
        """Test that an invalid WSDL definition raises a ValueError."""
        with pytest.raises(ValueError):
            ONVIFWSDL.get_definition(service, version)


class TestCacheModeIntegration:
    """Test CacheMode where it affects core integration."""

    @pytest.mark.parametrize(
        "cache_mode",
        [
            CacheMode.NONE,
            CacheMode.MEM,
            CacheMode.DB,
        ],
    )
    def test_operator_accepts_cache_modes(self, cache_mode):
        """ONVIFOperator accepts every supported cache mode."""
        definition = ONVIFWSDL.get_definition("devicemgmt")

        operator = ONVIFOperator(
            host="10.255.255.1",
            port=80,
            username="user",
            password="pass",
            wsdl_path=definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            cache=cache_mode,
        )

        assert operator.client is not None
