from onvif.services import AuthorizationServer
from base_service_test import ONVIFServiceTestBase


class TestAuthorizationServerWSDLCompliance(ONVIFServiceTestBase):
    """Test that AuthorizationServer service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = AuthorizationServer
    SERVICE_NAME = "security.authorizationserver"
    WSDL_PATH_COMPONENTS = [
        "ver10",
        "advancedsecurity",
        "wsdl",
        "advancedsecurity.wsdl",
    ]
    BINDING_NAME = "AuthorizationServerBinding"
    NAMESPACE_PREFIX = "tas"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/advancedsecurity/wsdl"
    XADDR_PATH = "/onvif/Security"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {
                "method": "GetAuthorizationServerConfigurations",
                "params": {"Token": None},
            },
            {
                "method": "GetAuthorizationServerConfigurations",
                "params": {"Token": "config1"},
            },
            {
                "method": "CreateAuthorizationServerConfiguration",
                "params": {
                    "Configuration": {
                        "Token": "auth_server_1",
                        "Name": "OAuth Server",
                        "ServerURI": "https://oauth.example.com",
                    }
                },
            },
            {
                "method": "SetAuthorizationServerConfiguration",
                "params": {
                    "Configuration": {
                        "Token": "auth_server_2",
                        "Name": "Updated OAuth Server",
                        "ServerURI": "https://oauth2.example.com",
                    }
                },
            },
            {
                "method": "DeleteAuthorizationServerConfiguration",
                "params": {"Token": "auth_server_3"},
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetAuthorizationServerConfigurations",
                "params": {"Token": "config_token1"},
            },
            {
                "method": "CreateAuthorizationServerConfiguration",
                "params": {
                    "Configuration": {
                        "Token": "new_auth",
                        "ServerURI": "https://auth.test.com",
                    }
                },
            },
            {
                "method": "SetAuthorizationServerConfiguration",
                "params": {
                    "Configuration": {
                        "Token": "existing_auth",
                        "ServerURI": "https://auth.updated.com",
                    }
                },
            },
            {
                "method": "DeleteAuthorizationServerConfiguration",
                "params": {"Token": "delete_auth"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
