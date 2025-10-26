from onvif.services import AccessRules
from base_service_test import ONVIFServiceTestBase


class TestAccessRulesWSDLCompliance(ONVIFServiceTestBase):
    """Test that AccessRules service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = AccessRules
    SERVICE_NAME = "accessrules"
    WSDL_PATH_COMPONENTS = ["ver10", "accessrules", "wsdl", "accessrules.wsdl"]
    BINDING_NAME = "AccessRulesBinding"
    NAMESPACE_PREFIX = "tar"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/accessrules/wsdl"
    XADDR_PATH = "/onvif/AccessRules"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {"method": "GetAccessProfileInfo", "params": {"Token": "token123"}},
            {
                "method": "GetAccessProfileInfoList",
                "params": {"Limit": 10, "StartReference": "ref1"},
            },
            {
                "method": "CreateAccessProfile",
                "params": {"AccessProfile": {"Token": "prof1", "Name": "Profile1"}},
            },
            {
                "method": "ModifyAccessProfile",
                "params": {
                    "AccessProfile": {"Token": "prof1", "Name": "Updated Profile"}
                },
            },
            {"method": "DeleteAccessProfile", "params": {"Token": "token456"}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetAccessProfiles",
                "params": {"Token": ["token1", "token2"]},
            },
            {
                "method": "DeleteAccessProfile",
                "params": {"Token": "token123"},
            },
            {
                "method": "ModifyAccessProfile",
                "params": {
                    "AccessProfile": {
                        "Token": "prof1",
                        "Name": "Updated Profile",
                    }
                },
            },
            {
                "method": "GetAccessProfileList",
                "params": {"Limit": 50, "StartReference": "profile123"},
            },
            {
                "method": "SetAccessProfile",
                "params": {
                    "AccessProfile": {
                        "Token": "prof1",
                        "Name": "Set Profile",
                    }
                },
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
