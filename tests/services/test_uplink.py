from onvif.services import Uplink
from base_service_test import ONVIFServiceTestBase


class TestUplinkWSDLCompliance(ONVIFServiceTestBase):
    """Test that Uplink service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Uplink
    SERVICE_NAME = "uplink"
    WSDL_PATH_COMPONENTS = ["ver10", "uplink", "wsdl", "uplink.wsdl"]
    BINDING_NAME = "UplinkBinding"
    NAMESPACE_PREFIX = "tul"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/uplink/wsdl"
    XADDR_PATH = "/onvif/Uplink"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {"method": "GetUplinks", "params": {}},
            {
                "method": "SetUplink",
                "params": {
                    "Configuration": {
                        "RemoteAddress": "192.168.1.100",
                        "LocalAddress": "192.168.1.50",
                        "Port": 8080,
                    }
                },
            },
            {
                "method": "DeleteUplink",
                "params": {"RemoteAddress": "192.168.1.100"},
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "SetUplink",
                "params": {
                    "Configuration": {
                        "RemoteAddress": "10.0.0.1",
                        "LocalAddress": "10.0.0.2",
                    }
                },
            },
            {
                "method": "DeleteUplink",
                "params": {"RemoteAddress": "10.0.0.1"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
