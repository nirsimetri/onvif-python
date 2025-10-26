from onvif.services import TLSServer
from base_service_test import ONVIFServiceTestBase


class TestTLSServerWSDLCompliance(ONVIFServiceTestBase):
    """Test that TLSServer service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = TLSServer
    SERVICE_NAME = "security.tlsserver"
    WSDL_PATH_COMPONENTS = [
        "ver10",
        "advancedsecurity",
        "wsdl",
        "advancedsecurity.wsdl",
    ]
    BINDING_NAME = "TLSServerBinding"
    NAMESPACE_PREFIX = "tas"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/advancedsecurity/wsdl"
    XADDR_PATH = "/onvif/Security"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {
                "method": "AddServerCertificateAssignment",
                "params": {"CertificationPathID": "certpath_1"},
            },
            {
                "method": "RemoveServerCertificateAssignment",
                "params": {"CertificationPathID": "certpath_2"},
            },
            {
                "method": "ReplaceServerCertificateAssignment",
                "params": {
                    "OldCertificationPathID": "old_path",
                    "NewCertificationPathID": "new_path",
                },
            },
            {"method": "GetAssignedServerCertificates", "params": {}},
            {
                "method": "SetEnabledTLSVersions",
                "params": {"Versions": ["1.2", "1.3"]},
            },
            {"method": "GetEnabledTLSVersions", "params": {}},
            {
                "method": "SetClientAuthenticationRequired",
                "params": {"clientAuthenticationRequired": True},
            },
            {"method": "GetClientAuthenticationRequired", "params": {}},
            {
                "method": "SetCnMapsToUser",
                "params": {"cnMapsToUser": True},
            },
            {"method": "GetCnMapsToUser", "params": {}},
            {
                "method": "AddCertPathValidationPolicyAssignment",
                "params": {"CertPathValidationPolicyID": "policy_1"},
            },
            {
                "method": "RemoveCertPathValidationPolicyAssignment",
                "params": {"CertPathValidationPolicyID": "policy_2"},
            },
            {
                "method": "ReplaceCertPathValidationPolicyAssignment",
                "params": {
                    "OldCertPathValidationPolicyID": "old_policy",
                    "NewCertPathValidationPolicyID": "new_policy",
                },
            },
            {"method": "GetAssignedCertPathValidationPolicies", "params": {}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "AddServerCertificateAssignment",
                "params": {"CertificationPathID": "test_cert_path"},
            },
            {
                "method": "RemoveServerCertificateAssignment",
                "params": {"CertificationPathID": "remove_cert_path"},
            },
            {
                "method": "ReplaceServerCertificateAssignment",
                "params": {
                    "OldCertificationPathID": "old_path_id",
                    "NewCertificationPathID": "new_path_id",
                },
            },
            {
                "method": "SetEnabledTLSVersions",
                "params": {"Versions": ["1.2", "1.3"]},
            },
            {
                "method": "SetClientAuthenticationRequired",
                "params": {"clientAuthenticationRequired": True},
            },
            {
                "method": "SetCnMapsToUser",
                "params": {"cnMapsToUser": False},
            },
            {
                "method": "AddCertPathValidationPolicyAssignment",
                "params": {"CertPathValidationPolicyID": "validation_policy_1"},
            },
            {
                "method": "RemoveCertPathValidationPolicyAssignment",
                "params": {"CertPathValidationPolicyID": "validation_policy_2"},
            },
            {
                "method": "ReplaceCertPathValidationPolicyAssignment",
                "params": {
                    "OldCertPathValidationPolicyID": "old_validation",
                    "NewCertPathValidationPolicyID": "new_validation",
                },
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
