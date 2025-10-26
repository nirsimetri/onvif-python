# onvif/services/security/keystore.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class Keystore(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.4 (August 2013) Release Notes
        # - KeystoreBinding (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl

        definition = ONVIFWSDL.get_definition("keystore")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def CreateRSAKeyPair(self, KeyLength, Alias=None):
        return self.operator.call("CreateRSAKeyPair", KeyLength=KeyLength, Alias=Alias)

    def CreateECCKeyPair(self, EllipticCurve, Alias=None):
        return self.operator.call(
            "CreateECCKeyPair", EllipticCurve=EllipticCurve, Alias=Alias
        )

    def UploadKeyPairInPKCS8(
        self,
        KeyPair,
        Alias=None,
        EncryptionPassphraseID=None,
        EncryptionPassphrase=None,
    ):
        return self.operator.call(
            "UploadKeyPairInPKCS8",
            KeyPair=KeyPair,
            Alias=Alias,
            EncryptionPassphraseID=EncryptionPassphraseID,
            EncryptionPassphrase=EncryptionPassphrase,
        )

    def UploadCertificateWithPrivateKeyInPKCS12(
        self,
        CertWithPrivateKey,
        CertificationPathAlias=None,
        KeyAlias=None,
        IgnoreAdditionalCertificates=None,
        IntegrityPassphraseID=None,
        EncryptionPassphraseID=None,
        Passphrase=None,
    ):
        return self.operator.call(
            "UploadCertificateWithPrivateKeyInPKCS12",
            CertWithPrivateKey=CertWithPrivateKey,
            CertificationPathAlias=CertificationPathAlias,
            KeyAlias=KeyAlias,
            IgnoreAdditionalCertificates=IgnoreAdditionalCertificates,
            IntegrityPassphraseID=IntegrityPassphraseID,
            EncryptionPassphraseID=EncryptionPassphraseID,
            Passphrase=Passphrase,
        )

    def GetKeyStatus(self, KeyID):
        return self.operator.call("GetKeyStatus", KeyID=KeyID)

    def GetPrivateKeyStatus(self, KeyID):
        return self.operator.call("GetPrivateKeyStatus", KeyID=KeyID)

    def GetAllKeys(self):
        return self.operator.call("GetAllKeys")

    def DeleteKey(self, KeyID):
        return self.operator.call("DeleteKey", KeyID=KeyID)

    def CreatePKCS10CSR(self, Subject, KeyID, SignatureAlgorithm, CSRAttribute=None):
        return self.operator.call(
            "CreatePKCS10CSR",
            Subject=Subject,
            KeyID=KeyID,
            CSRAttribute=CSRAttribute,
            SignatureAlgorithm=SignatureAlgorithm,
        )

    def CreateSelfSignedCertificate(
        self,
        Subject,
        KeyID,
        SignatureAlgorithm,
        X509Version=None,
        Alias=None,
        notValidBefore=None,
        notValidAfter=None,
        Extension=None,
    ):
        return self.operator.call(
            "CreateSelfSignedCertificate",
            X509Version=X509Version,
            Subject=Subject,
            KeyID=KeyID,
            Alias=Alias,
            notValidBefore=notValidBefore,
            notValidAfter=notValidAfter,
            SignatureAlgorithm=SignatureAlgorithm,
            Extension=Extension,
        )

    def UploadCertificate(
        self, Certificate, Alias=None, KeyAlias=None, PrivateKeyRequired=None
    ):
        return self.operator.call(
            "UploadCertificate",
            Certificate=Certificate,
            Alias=Alias,
            KeyAlias=KeyAlias,
            PrivateKeyRequired=PrivateKeyRequired,
        )

    def GetCertificate(self, CertificateID):
        return self.operator.call("GetCertificate", CertificateID=CertificateID)

    def GetAllCertificates(self):
        return self.operator.call("GetAllCertificates")

    def DeleteCertificate(self, CertificateID):
        return self.operator.call("DeleteCertificate", CertificateID=CertificateID)

    def CreateCertificationPath(self, CertificateIDs, Alias=None):
        return self.operator.call(
            "CreateCertificationPath", CertificateIDs=CertificateIDs, Alias=Alias
        )

    def GetCertificationPath(self, CertificationPathID):
        return self.operator.call(
            "GetCertificationPath", CertificationPathID=CertificationPathID
        )

    def GetAllCertificationPaths(self):
        return self.operator.call("GetAllCertificationPaths")

    def SetCertificationPath(self, CertificationPathID, CertificationPath):
        return self.operator.call(
            "SetCertificationPath",
            CertificationPathID=CertificationPathID,
            CertificationPath=CertificationPath,
        )

    def DeleteCertificationPath(self, CertificationPathID):
        return self.operator.call(
            "DeleteCertificationPath", CertificationPathID=CertificationPathID
        )

    def UploadPassphrase(self, Passphrase, PassphraseAlias=None):
        return self.operator.call(
            "UploadPassphrase", Passphrase=Passphrase, PassphraseAlias=PassphraseAlias
        )

    def GetAllPassphrases(self):
        return self.operator.call("GetAllPassphrases")

    def DeletePassphrase(self, PassphraseID):
        return self.operator.call("DeletePassphrase", PassphraseID=PassphraseID)

    def UploadCRL(self, Crl, Alias=None, anyParameters=None):
        return self.operator.call(
            "UploadCRL", Crl=Crl, Alias=Alias, anyParameters=anyParameters
        )

    def GetCRL(self, CrlID):
        return self.operator.call("GetCRL", CrlID=CrlID)

    def GetAllCRLs(self):
        return self.operator.call("GetAllCRLs")

    def DeleteCRL(self, CrlID):
        return self.operator.call("DeleteCRL", CrlID=CrlID)

    def CreateCertPathValidationPolicy(
        self, Parameters, TrustAnchor, Alias=None, anyParameters=None
    ):
        return self.operator.call(
            "CreateCertPathValidationPolicy",
            Alias=Alias,
            Parameters=Parameters,
            TrustAnchor=TrustAnchor,
            anyParameters=anyParameters,
        )

    def GetCertPathValidationPolicy(self, CertPathValidationPolicyID):
        return self.operator.call(
            "GetCertPathValidationPolicy",
            CertPathValidationPolicyID=CertPathValidationPolicyID,
        )

    def GetAllCertPathValidationPolicies(self):
        return self.operator.call("GetAllCertPathValidationPolicies")

    def SetCertPathValidationPolicy(
        self, CertPathValidationPolicy, CertPathValidationPolicyID=None
    ):
        return self.operator.call(
            "SetCertPathValidationPolicy",
            CertPathValidationPolicyID=CertPathValidationPolicyID,
            CertPathValidationPolicy=CertPathValidationPolicy,
        )

    def DeleteCertPathValidationPolicy(self, CertPathValidationPolicyID):
        return self.operator.call(
            "DeleteCertPathValidationPolicy",
            CertPathValidationPolicyID=CertPathValidationPolicyID,
        )
