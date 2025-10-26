from onvif.services import JWT
from base_service_test import ONVIFServiceTestBase


class TestJWTWSDLCompliance(ONVIFServiceTestBase):
    """Test that JWT service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = JWT
    SERVICE_NAME = "security.jwt"
    WSDL_PATH_COMPONENTS = [
        "ver10",
        "advancedsecurity",
        "wsdl",
        "advancedsecurity.wsdl",
    ]
    BINDING_NAME = "JWTBinding"
    NAMESPACE_PREFIX = "tas"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/advancedsecurity/wsdl"
    XADDR_PATH = "/onvif/Security"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetJWTConfiguration", "params": {}},
            {
                "method": "SetJWTConfiguration",
                "params": {
                    "Configuration": {
                        "TokenIssuer": "https://issuer.example.com",
                        "Audience": "onvif-device",
                        "PublicKey": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----",
                    }
                },
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "SetJWTConfiguration",
                "params": {
                    "Configuration": {
                        "TokenIssuer": "https://auth.test.com",
                        "Audience": "test-device",
                    }
                },
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
