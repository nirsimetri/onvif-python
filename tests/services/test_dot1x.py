from onvif.services import Dot1X
from base_service_test import ONVIFServiceTestBase


class TestDot1XWSDLCompliance(ONVIFServiceTestBase):
    """Test that Dot1X service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Dot1X
    SERVICE_NAME = "security.dot1x"
    WSDL_PATH_COMPONENTS = [
        "ver10",
        "advancedsecurity",
        "wsdl",
        "advancedsecurity.wsdl",
    ]
    BINDING_NAME = "Dot1XBinding"
    NAMESPACE_PREFIX = "tas"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/advancedsecurity/wsdl"
    XADDR_PATH = "/onvif/Security"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {
                "method": "AddDot1XConfiguration",
                "params": {
                    "Dot1XConfiguration": {
                        "Dot1XConfigurationToken": "dot1x_config_1",
                        "Identity": "user@example.com",
                    }
                },
            },
            {"method": "GetAllDot1XConfigurations", "params": {}},
            {"method": "GetDot1XConfiguration", "params": {"Dot1XID": "dot1x_id_1"}},
            {"method": "DeleteDot1XConfiguration", "params": {"Dot1XID": "dot1x_id_2"}},
            {
                "method": "SetNetworkInterfaceDot1XConfiguration",
                "params": {"token": "eth0", "Dot1XID": "dot1x_id_3"},
            },
            {
                "method": "GetNetworkInterfaceDot1XConfiguration",
                "params": {"token": "eth1"},
            },
            {
                "method": "DeleteNetworkInterfaceDot1XConfiguration",
                "params": {"token": "eth2"},
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "AddDot1XConfiguration",
                "params": {
                    "Dot1XConfiguration": {
                        "Dot1XConfigurationToken": "config_1",
                        "Identity": "test@test.com",
                    }
                },
            },
            {
                "method": "GetDot1XConfiguration",
                "params": {"Dot1XID": "dot1x_1"},
            },
            {
                "method": "DeleteDot1XConfiguration",
                "params": {"Dot1XID": "dot1x_2"},
            },
            {
                "method": "SetNetworkInterfaceDot1XConfiguration",
                "params": {"token": "eth0", "Dot1XID": "dot1x_3"},
            },
            {
                "method": "GetNetworkInterfaceDot1XConfiguration",
                "params": {"token": "eth1"},
            },
            {
                "method": "DeleteNetworkInterfaceDot1XConfiguration",
                "params": {"token": "eth2"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
