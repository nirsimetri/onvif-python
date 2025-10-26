from onvif.services import Provisioning
from base_service_test import ONVIFServiceTestBase


class TestProvisioningWSDLCompliance(ONVIFServiceTestBase):
    """Test that Provisioning service implementation matches WSDL specification."""

    # Service configuration
    SERVICE_CLASS = Provisioning
    SERVICE_NAME = "provisioning"
    WSDL_PATH_COMPONENTS = ["ver10", "provisioning", "wsdl", "provisioning.wsdl"]
    BINDING_NAME = "ProvisioningBinding"
    NAMESPACE_PREFIX = "tpv"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/provisioning/wsdl"
    XADDR_PATH = "/onvif/Provisioning"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {
                "method": "PanMove",
                "params": {
                    "VideoSource": "vs1",
                    "Direction": "Left",
                    "Timeout": "PT5S",
                },
            },
            {
                "method": "TiltMove",
                "params": {"VideoSource": "vs2", "Direction": "Up", "Timeout": "PT3S"},
            },
            {
                "method": "ZoomMove",
                "params": {
                    "VideoSource": "vs3",
                    "Direction": "Wide",
                    "Timeout": "PT10S",
                },
            },
            {
                "method": "RollMove",
                "params": {
                    "VideoSource": "vs4",
                    "Direction": "Clockwise",
                    "Timeout": "PT7S",
                },
            },
            {
                "method": "FocusMove",
                "params": {
                    "VideoSource": "vs5",
                    "Direction": "Near",
                    "Timeout": "PT4S",
                },
            },
            {"method": "Stop", "params": {"VideoSource": "vs6"}},
            {"method": "GetUsage", "params": {"VideoSource": "vs7"}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "PanMove",
                "params": {
                    "VideoSource": "vs1",
                    "Direction": "Right",
                    "Timeout": "PT6S",
                },
            },
            {
                "method": "TiltMove",
                "params": {
                    "VideoSource": "vs2",
                    "Direction": "Down",
                    "Timeout": "PT8S",
                },
            },
            {
                "method": "ZoomMove",
                "params": {
                    "VideoSource": "vs3",
                    "Direction": "Tele",
                    "Timeout": "PT12S",
                },
            },
            {
                "method": "RollMove",
                "params": {
                    "VideoSource": "vs4",
                    "Direction": "CounterClockwise",
                    "Timeout": "PT5S",
                },
            },
            {
                "method": "FocusMove",
                "params": {"VideoSource": "vs5", "Direction": "Far", "Timeout": "PT9S"},
            },
            {
                "method": "Stop",
                "params": {"VideoSource": "vs6"},
            },
            {
                "method": "GetUsage",
                "params": {"VideoSource": "vs7"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
