from onvif.services import Credential
from base_service_test import ONVIFServiceTestBase


class TestCredentialWSDLCompliance(ONVIFServiceTestBase):
    """Test that Credential service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Credential
    SERVICE_NAME = "credential"
    WSDL_PATH_COMPONENTS = ["ver10", "credential", "wsdl", "credential.wsdl"]
    BINDING_NAME = "CredentialBinding"
    NAMESPACE_PREFIX = "tcr"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/credential/wsdl"
    XADDR_PATH = "/onvif/Credential"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {
                "method": "GetSupportedFormatTypes",
                "params": {"CredentialIdentifierTypeName": "Card"},
            },
            {"method": "GetCredentialInfo", "params": {"Token": "cred_token"}},
            {
                "method": "GetCredentialInfoList",
                "params": {"Limit": 10, "StartReference": "ref1"},
            },
            {
                "method": "CreateCredential",
                "params": {
                    "Credential": {"Token": "cred1", "Name": "Credential1"},
                    "State": "Enabled",
                },
            },
            {
                "method": "ModifyCredential",
                "params": {
                    "Credential": {"Token": "cred1", "Name": "Modified Credential"}
                },
            },
            {"method": "DeleteCredential", "params": {"Token": "cred_delete"}},
            {"method": "GetCredentialState", "params": {"Token": "cred_state"}},
            {
                "method": "EnableCredential",
                "params": {"Token": "cred_enable", "Reason": "Testing"},
            },
            {
                "method": "DisableCredential",
                "params": {"Token": "cred_disable", "Reason": "Suspended"},
            },
            {
                "method": "ResetAntipassbackViolation",
                "params": {"CredentialToken": "apb_token"},
            },
            {
                "method": "GetCredentialIdentifiers",
                "params": {"CredentialToken": "ident_token"},
            },
            {
                "method": "SetCredentialIdentifier",
                "params": {
                    "CredentialToken": "set_token",
                    "CredentialIdentifier": {"Type": "Card", "Value": "12345"},
                },
            },
            {
                "method": "GetWhitelist",
                "params": {
                    "Limit": 20,
                    "StartReference": "wl_ref",
                    "IdentifierType": "Card",
                    "FormatType": "RFID",
                    "Value": None,
                },
            },
            {
                "method": "AddToWhitelist",
                "params": {"Identifier": {"Type": "Card", "Value": "WL123"}},
            },
            {"method": "DeleteWhitelist"},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetSupportedFormatTypes",
                "params": {"CredentialIdentifierTypeName": "Card"},
            },
            {
                "method": "GetCredentialInfo",
                "params": {"Token": "info_token"},
            },
            {
                "method": "GetCredentialList",
                "params": {"Limit": 50, "StartReference": "list_ref"},
            },
            {
                "method": "CreateCredential",
                "params": {
                    "Credential": {"Token": "new_cred", "Name": "New"},
                    "State": "Enabled",
                },
            },
            {
                "method": "SetCredential",
                "params": {"CredentialData": {"Token": "set_cred", "Data": "data"}},
            },
            {
                "method": "EnableCredential",
                "params": {"Token": "enable_token", "Reason": "Activated"},
            },
            {
                "method": "SetCredentialIdentifier",
                "params": {
                    "CredentialToken": "ident_token",
                    "CredentialIdentifier": {"Type": "Card", "Value": "123"},
                },
            },
            {
                "method": "DeleteCredentialIdentifier",
                "params": {
                    "CredentialToken": "del_ident_token",
                    "CredentialIdentifierTypeName": "Card",
                },
            },
            {
                "method": "GetCredentialAccessProfiles",
                "params": {"CredentialToken": "access_token"},
            },
            {
                "method": "SetCredentialAccessProfiles",
                "params": {
                    "CredentialToken": "set_access_token",
                    "CredentialAccessProfile": {"ProfileToken": "prof1"},
                },
            },
            {
                "method": "GetWhitelist",
                "params": {
                    "Limit": 30,
                    "StartReference": "wl_start",
                    "IdentifierType": "Card",
                    "FormatType": "RFID",
                    "Value": "12345",
                },
            },
            {
                "method": "AddToBlacklist",
                "params": {"Identifier": {"Type": "Card", "Value": "BL456"}},
            },
            {
                "method": "RemoveFromWhitelist",
                "params": {"Identifier": {"Type": "Card", "Value": "WL789"}},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
