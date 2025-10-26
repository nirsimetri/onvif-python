from onvif.services import AccessControl
from base_service_test import ONVIFServiceTestBase


class TestAccessControlWSDLCompliance(ONVIFServiceTestBase):
    """Test that AccessControl service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = AccessControl
    SERVICE_NAME = "accesscontrol"
    WSDL_PATH_COMPONENTS = ["ver10", "pacs", "accesscontrol.wsdl"]
    BINDING_NAME = "PACSBinding"
    NAMESPACE_PREFIX = "tac"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/accesscontrol/wsdl"
    XADDR_PATH = "/onvif/AccessControl"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {"method": "GetAccessPointInfo", "params": {"Token": "token123"}},
            {
                "method": "GetAccessPointInfoList",
                "params": {"Limit": 10, "StartReference": "ref1"},
            },
            {
                "method": "CreateAccessPoint",
                "params": {"AccessPoint": {"Token": "ap1", "Name": "Door1"}},
            },
            {
                "method": "SetAccessPointAuthenticationProfile",
                "params": {
                    "Token": "token123",
                    "AuthenticationProfileToken": "auth123",
                },
            },
            {
                "method": "ExternalAuthorization",
                "params": {
                    "AccessPointToken": "ap123",
                    "Decision": "Granted",
                    "CredentialToken": "cred123",
                    "Reason": "Authorized",
                },
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetAccessPoints",
                "params": {"Token": ["token1", "token2"]},
            },
            {
                "method": "DeleteAccessPoint",
                "params": {"Token": "token123"},
            },
            {
                "method": "ModifyAccessPoint",
                "params": {
                    "AccessPoint": {
                        "Token": "ap1",
                        "Name": "Updated Door",
                        "Enabled": True,
                    }
                },
            },
            {
                "method": "GetAreaList",
                "params": {"Limit": 50, "StartReference": "area123"},
            },
            {
                "method": "EnableAccessPoint",
                "params": {"Token": "ap1"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
