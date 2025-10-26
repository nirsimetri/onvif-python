from onvif.services import MediaSigning
from base_service_test import ONVIFServiceTestBase


class TestMediaSigningWSDLCompliance(ONVIFServiceTestBase):
    """Test that MediaSigning service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = MediaSigning
    SERVICE_NAME = "security.mediasigning"
    WSDL_PATH_COMPONENTS = [
        "ver10",
        "advancedsecurity",
        "wsdl",
        "advancedsecurity.wsdl",
    ]
    BINDING_NAME = "MediaSigningBinding"
    NAMESPACE_PREFIX = "tas"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/advancedsecurity/wsdl"
    XADDR_PATH = "/onvif/Security"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {
                "method": "AddMediaSigningCertificateAssignment",
                "params": {"CertificationPathID": "cert_path_1"},
            },
            {
                "method": "RemoveMediaSigningCertificateAssignment",
                "params": {"CertificationPathID": "cert_path_2"},
            },
            {"method": "GetAssignedMediaSigningCertificates", "params": {}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "AddMediaSigningCertificateAssignment",
                "params": {"CertificationPathID": "test_cert_path_1"},
            },
            {
                "method": "RemoveMediaSigningCertificateAssignment",
                "params": {"CertificationPathID": "test_cert_path_2"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
