from onvif.services import AdvancedSecurity
from base_service_test import ONVIFServiceTestBase


class TestAdvancedSecurityWSDLCompliance(ONVIFServiceTestBase):
    """Test that AdvancedSecurity service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = AdvancedSecurity
    SERVICE_NAME = "security.advancedsecurity"
    WSDL_PATH_COMPONENTS = [
        "ver10",
        "advancedsecurity",
        "wsdl",
        "advancedsecurity.wsdl",
    ]
    BINDING_NAME = "AdvancedSecurityServiceBinding"
    NAMESPACE_PREFIX = "tas"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/advancedsecurity/wsdl"
    XADDR_PATH = "/onvif/Security"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetServiceCapabilities",
                "params": {},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
