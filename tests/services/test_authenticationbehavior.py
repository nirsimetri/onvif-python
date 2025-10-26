from onvif.services import AuthenticationBehavior
from base_service_test import ONVIFServiceTestBase


class TestAuthenticationBehaviorWSDLCompliance(ONVIFServiceTestBase):
    """Test that AuthenticationBehavior service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = AuthenticationBehavior
    SERVICE_NAME = "authenticationbehavior"
    WSDL_PATH_COMPONENTS = [
        "ver10",
        "authenticationbehavior",
        "wsdl",
        "authenticationbehavior.wsdl",
    ]
    BINDING_NAME = "AuthenticationBehaviorBinding"
    NAMESPACE_PREFIX = "tab"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/authenticationbehavior/wsdl"
    XADDR_PATH = "/onvif/AuthenticationBehavior"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {"method": "GetAuthenticationProfileInfo", "params": {"Token": "token123"}},
            {
                "method": "GetAuthenticationProfileInfoList",
                "params": {"Limit": 10, "StartReference": "ref1"},
            },
            {
                "method": "GetAuthenticationProfiles",
                "params": {"Token": ["token1", "token2"]},
            },
            {
                "method": "CreateAuthenticationProfile",
                "params": {
                    "AuthenticationProfile": {"Token": "prof1", "Name": "Profile1"}
                },
            },
            {
                "method": "ModifyAuthenticationProfile",
                "params": {
                    "AuthenticationProfile": {"Token": "prof1", "Name": "Modified"}
                },
            },
            {"method": "DeleteAuthenticationProfile", "params": {"Token": "token456"}},
            {"method": "GetSecurityLevelInfo", "params": {"Token": "sec_token"}},
            {
                "method": "GetSecurityLevelInfoList",
                "params": {"Limit": 20, "StartReference": "sec_ref"},
            },
            {
                "method": "CreateSecurityLevel",
                "params": {"SecurityLevel": {"Token": "sec1", "Name": "Level1"}},
            },
            {
                "method": "SetSecurityLevel",
                "params": {"SecurityLevel": {"Token": "sec1", "Name": "SetLevel"}},
            },
            {"method": "DeleteSecurityLevel", "params": {"Token": "sec_delete"}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetAuthenticationProfileInfo",
                "params": {"Token": "token_info"},
            },
            {
                "method": "GetAuthenticationProfileInfoList",
                "params": {"Limit": 50, "StartReference": "ref_list"},
            },
            {
                "method": "CreateAuthenticationProfile",
                "params": {
                    "AuthenticationProfile": {
                        "Token": "new_prof",
                        "Name": "New Profile",
                    }
                },
            },
            {
                "method": "ModifyAuthenticationProfile",
                "params": {
                    "AuthenticationProfile": {
                        "Token": "mod_prof",
                        "Name": "Modified Profile",
                    }
                },
            },
            {
                "method": "DeleteAuthenticationProfile",
                "params": {"Token": "delete_token"},
            },
            {
                "method": "GetSecurityLevelInfo",
                "params": {"Token": "sec_info_token"},
            },
            {
                "method": "GetSecurityLevelList",
                "params": {"Limit": 30, "StartReference": "sec_ref"},
            },
            {
                "method": "CreateSecurityLevel",
                "params": {"SecurityLevel": {"Token": "sec_new", "Name": "New Level"}},
            },
            {
                "method": "ModifySecurityLevel",
                "params": {
                    "SecurityLevel": {"Token": "sec_mod", "Name": "Modified Level"}
                },
            },
            {
                "method": "DeleteSecurityLevel",
                "params": {"Token": "sec_delete_token"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
