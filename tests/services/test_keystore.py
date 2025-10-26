from onvif.services import Keystore
from base_service_test import ONVIFServiceTestBase


class TestKeystoreWSDLCompliance(ONVIFServiceTestBase):
    """Test that Keystore service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Keystore
    SERVICE_NAME = "security.keystore"
    WSDL_PATH_COMPONENTS = [
        "ver10",
        "advancedsecurity",
        "wsdl",
        "advancedsecurity.wsdl",
    ]
    BINDING_NAME = "KeystoreBinding"
    NAMESPACE_PREFIX = "tas"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/advancedsecurity/wsdl"
    XADDR_PATH = "/onvif/Security"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {
                "method": "CreateRSAKeyPair",
                "params": {"KeyLength": 2048, "Alias": "RSA_Key_1"},
            },
            {
                "method": "CreateECCKeyPair",
                "params": {"EllipticCurve": "secp256r1", "Alias": "ECC_Key_1"},
            },
            {"method": "GetKeyStatus", "params": {"KeyID": "key_1"}},
            {"method": "GetAllKeys", "params": {}},
            {"method": "DeleteKey", "params": {"KeyID": "key_2"}},
            {
                "method": "UploadCertificate",
                "params": {
                    "Certificate": "base64_cert_data",
                    "Alias": "Cert_1",
                    "KeyAlias": "key_3",
                    "PrivateKeyRequired": None,
                },
            },
            {"method": "GetCertificate", "params": {"CertificateID": "cert_1"}},
            {"method": "GetAllCertificates", "params": {}},
            {"method": "DeleteCertificate", "params": {"CertificateID": "cert_2"}},
            {
                "method": "CreateCertificationPath",
                "params": {
                    "CertificateIDs": ["cert_1", "cert_2", "cert_3"],
                    "Alias": "CertPath_1",
                },
            },
            {"method": "GetAllCertificationPaths", "params": {}},
            {
                "method": "UploadPassphrase",
                "params": {"Passphrase": "MySecretPass", "PassphraseAlias": "Pass_1"},
            },
            {"method": "GetAllPassphrases", "params": {}},
            {
                "method": "CreateSelfSignedCertificate",
                "params": {
                    "Subject": "CN=Test Device",
                    "KeyID": "key_1",
                    "SignatureAlgorithm": "sha256WithRSAEncryption",
                    "X509Version": None,
                    "Alias": "SelfSignedCert_1",
                    "notValidBefore": None,
                    "notValidAfter": None,
                    "Extension": None,
                },
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "CreateRSAKeyPair",
                "params": {"KeyLength": 4096, "Alias": "TestKey"},
            },
            {
                "method": "GetKeyStatus",
                "params": {"KeyID": "test_key_id"},
            },
            {
                "method": "DeleteKey",
                "params": {"KeyID": "delete_key_id"},
            },
            {
                "method": "GetCertificate",
                "params": {"CertificateID": "test_cert_id"},
            },
            {
                "method": "DeleteCertificate",
                "params": {"CertificateID": "delete_cert_id"},
            },
            {
                "method": "CreateCertificationPath",
                "params": {
                    "CertificateIDs": ["cert1", "cert2"],
                    "Alias": "TestPath",
                },
            },
            {
                "method": "UploadPassphrase",
                "params": {"Passphrase": "secret", "PassphraseAlias": "TestPass"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)

    def test_keystore_operations_count(self):
        """Informational test to show the number of Keystore operations."""
        wsdl_operations = self.get_wsdl_operations()
        implemented_methods = self.get_implemented_methods()

        print(
            f"\nKeystore WSDL contains {len(wsdl_operations)} operations, "
            f"{len(implemented_methods)} methods implemented"
        )
