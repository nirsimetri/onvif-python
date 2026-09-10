"""Security (Keystore) service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-many-public-methods
class Keystore(ONVIFService):
    """Security (Keystore) service client.

    | Property | Details |
    | --- | --- |
    | **First introduced** | ONVIF Release 2.4 (August 2013) |
    | **Binding name** | `KeystoreBinding` (`ver10/advancedsecurity/wsdl/advancedsecurity.wsdl`) |
    | **Operations** | [advancedsecurity.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl) |
    | **Specification** | [Security.xml](https://developer.onvif.org/pub/specs/branches/development/doc/Security.xml) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("keystore")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def CreateRSAKeyPair(self, KeyLength, Alias=None):
        """This operation triggers the asynchronous generation of an RSA key pair of a
        particular key length (specified as the number of bits) as specified in [RFC
        3447], with a suitable key generation mechanism on the device.

        Keys, especially RSA key pairs, are uniquely identified using key IDs.

        If the device does not have not enough storage capacity for storing the key pair
        to be created, the maximum number of keys reached fault shall be produced and no
        key pair shall be generated. Otherwise, the operation generates a keyID for the
        new key and associates the generating status to it.

        Immediately after key generation has started, the device shall return the keyID
        to the client and continue to generate the key pair. The client may query the
        device with the GetKeyStatus operation whether the generation has finished. The
        client may also subscribe to Key Status events to be notified about key status
        changes.

        The device also returns a best-effort estimate of how much time it requires to
        create the key pair. A client may use this information as an indication how long
        to wait before querying the device whether key generation is completed.

        After the key has been successfully created, the device shall assign it the ok
        status. If the key generation fails, the device shall assign the key the corrupt
        status.
        """
        return self.operator.call("CreateRSAKeyPair", KeyLength=KeyLength, Alias=Alias)

    def CreateECCKeyPair(self, EllipticCurve, Alias=None):
        """This operation triggers the asynchronous generation of an ECC key pair using
        a particular elliptic curve as specified in [RFC 8422], with a suitable key
        generation mechanism on the device.

        Keys, especially ECC key pairs, are uniquely identified using key IDs.

        If the device does not have not enough storage capacity for storing the key pair
        to be created, the maximum number of keys reached fault shall be produced and no
        key pair shall be generated. Otherwise, the operation generates a keyID for the
        new key and associates the generating status to it.

        Immediately after key generation has started, the device shall return the keyID
        to the client and continue to generate the key pair. The client may query the
        device with the GetKeyStatus operation whether the generation has finished. The
        client may also subscribe to Key Status events to be notified about key status
        changes.

        The device also returns a best-effort estimate of how much time it requires to
        create the key pair. A client may use this information as an indication how long
        to wait before querying the device whether key generation is completed.

        After the key has been successfully created, the device shall assign it the ok
        status. If the key generation fails, the device shall assign the key the corrupt
        status.
        """
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
        """Deprecated method for uploading a key pair in a PKCS#8 data structure as
        specified in [RFC 5958, RFC 5959].

        If an encryption passphrase ID is supplied in the request, the device shall
        assume that the KeyPair parameter contains an EncryptedPrivateKeyInfo ASN.1
        structure that is encrypted under the passphrase in the keystore that
        corresponds to the supplied ID, where the EncryptedPrivateKeyInfo structure
        contains both the private key and the corresponding public key. If no encryption
        passphrase ID is supplied, the device shall assume that the KeyPair parameter
        contains a OneAsymmetricKey ASN.1 structure which contains both the private key
        and the corresponding public key.
        """
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
        """This operation uploads a certification path consisting of X.509 certificates
        as specified by [RFC 5280] in DER encoding along with a private key to a
        device’s keystore.

        Certificates and private key are supplied in the form of a PKCS#12 file as
        specified in [PKCS#12].

        The device shall support PKCS#12 files that contain the following safe bags:

        - one or more instances of CertBag [PKCS#12, Sect. 4.2.3]
        - either exactly one instance of KeyBag [PKCS#12, Sect. 4.3.1] or exactly one
        instance of PKCS8ShroudedKeyBag [PKCS#12, Sect. 4.2.2].

        If the IgnoreAdditionalCertificates parameter has the value true, the device shall
        behave as if the client had supplied only the first CertBag in the sequence of
        CertBag instances. The device shall support PKCS#12 passphrase integrity mode for
        integrity protection of the PKCS#12 PFX as specified in [PKCS#12, Sect. 4]. The device
        shall support PKCS8ShroudedKeyBags that are encrypted with the same passphrase as the
        CertBag instances. If an integrity passphrase ID is supplied, the device shall use the
        corresponding passphrase in the keystore to check the integrity of the supplied
        PKCS#12 PFX. If an integrity passphrase ID is supplied, but the supplied PKCS#12 PFX
        has no integrity protection, the device shall produce a BadPKCS12File fault and shall
        not store the uploaded certificates nor the uploaded key pair in the keystore. If an
        encryption passphrase ID is supplied, the device shall use the corresponding passphrase
        in the keystore to decrypt the PKCS8ShroudedKeyBag and the CertBag instances. If an
        EncryptionPassphraseID is supplied, but a CertBag is not encrypted, the device shall
        ignore the supplied EncryptionPassphraseID when processing this CertBag. If an
        EncryptionPassphraseID is supplied, but a KeyBag is provided instead of a
        PKCS8ShroudedKeyBag, the device shall ignore the supplied EncryptionPassphraseID
        when processing the KeyBag.
        """
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
        """This operation returns the status of a key.

        Keys are uniquely identified using key IDs. If no key is stored under the
        requested key ID in the keystore, an InvalidKeyID fault is produced. Otherwise,
        the status of the key is returned.
        """
        return self.operator.call("GetKeyStatus", KeyID=KeyID)

    def GetPrivateKeyStatus(self, KeyID):
        """This operation returns whether a key pair contains a private key.

        Keys are uniquely identified using key IDs. If no key is stored under the
        requested key ID in the keystore or the key identified by the requested key ID
        does not identify a key pair, the device shall produce an InvalidKeyID fault.
        Otherwise, this operation returns true if the key pair identified by the key ID
        contains a private key, and false otherwise.
        """
        return self.operator.call("GetPrivateKeyStatus", KeyID=KeyID)

    def GetAllKeys(self):
        """This operation returns information about all keys that are stored in the
        device’s keystore.

        This operation may be used, e.g., if a client lost track of which keys are
        present on the device. If no key is stored on the device, an empty list is
        returned.
        """
        return self.operator.call("GetAllKeys")

    def DeleteKey(self, KeyID):
        """This operation deletes a key from the device’s keystore.

        Keys are uniquely identified using key IDs. If no key is stored under the
        requested key ID in the keystore, a device shall produce an InvalidArgVal fault.
        If a reference exists for the specified key, a device shall produce the
        corresponding fault and shall not delete the key. If there is a key under the
        requested key ID stored in the keystore and the key could not be deleted, a
        device shall produce a KeyDeletion fault. If the key has the status generating,
        a device shall abort the generation of the key and delete from the keystore all
        data generated for this key. After a key is successfully deleted, the device may
        assign its former ID to other keys.
        """
        return self.operator.call("DeleteKey", KeyID=KeyID)

    def CreatePKCS10CSR(self, Subject, KeyID, SignatureAlgorithm, CSRAttribute=None):
        """This operation generates a DER-encoded PKCS#10 v1.7 certification request
        (sometimes also called certificate signing request or CSR) as specified in RFC
        2986 for a public key on the device.

        The key pair that contains the public key for which a certification request
        shall be produced is specified by its key ID. If no key is stored under the
        requested KeyID or the key specified by the requested KeyID is not an asymmetric
        key pair, an invalid key ID fault shall be produced and no CSR shall be
        generated.

        A device that supports this command shall as minimum support the
        sha-1WithRSAEncryption signature algorithm as specified in RFC 3279. If the
        specified signature algorithm is not supported by the device, an
        UnsupportedSignatureAlgorithm fault shall be produced and no CSR shall be
        generated.

        If the public key identified by the requested Key ID is an invalid input to the
        specified signature algorithm, a KeySignatureAlgorithmMismatch fault shall be
        produced and no CSR shall be generated. If the key pair does not have status ok,
        a device shall produce an InvalidKeyStatus fault and no CSR shall be generated.
        """
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
        """This operation generates for a public key on the device a self-signed X.509
        certificate that complies to RFC 5280.

        The X509Version parameter specifies the version of X.509 that the generated
        certificate shall comply to. A device that supports this command shall support
        the generation of X.509v3 certificates as specified in RFC 5280 and may
        additionally be able to handle other X.509 certificate formats as indicated by
        the X.509Versions capability.

        The key pair that contains the public key for which a self-signed certificate
        shall be produced is specified by its key pair ID. The subject parameter
        describes the entity that the public key belongs to. If the key pair does not
        have status ok, a device shall produce an InvalidKeyStatus fault and no
        certificate shall be generated. The signature algorithm parameter determines
        which signature algorithm shall be used for signing the certification request
        with the public key specified by the key ID parameter. A device that supports
        this command shall as minimum support the sha-1WithRSAEncryption signature
        algorithm as specified in RFC 3279. The Extensions parameter specifies potential
        X509v3 extensions that shall be contained in the certificate. A device that
        supports this command shall support the extensions that are defined in [RFC
        5280], Sect. 4.2] as mandatory for CAs that issue self-signed certificates.

        Certificates are uniquely identified using certificate IDs. If the command was
        successful, the device generates a new ID for the generated certificate and
        returns this ID.

        If the device does not have not enough storage capacity for storing the
        certificate to be created, the maximum number of certificates reached fault
        shall be produced and no certificate shall be generated.
        """
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
        """This operation uploads an X.509 certificate as specified by [RFC 5280] in DER
        encoding and the public key in the certificate to a device’s keystore.

        A device that supports this command shall be able to handle X.509v3 certificates
        as specified in RFC 5280 and may additionally be able to handle other X.509
        certificate formats as indicated by the X.509Versions capability. A device that
        supports this command shall support sha1-WithRSAEncryption as certificate
        signature algorithm.

        Certificates are uniquely identified using certificate IDs, and key pairs are
        uniquely identified using key IDs. The device shall generate a new certificate
        ID for the uploaded certificate.

        Certain certificate usages, e.g. TLS server authentication, require the private
        key that corresponds to the public key in the certificate to be present in the
        keystore. In such cases, the client may indicate that it expects the device to
        produce a fault if the matching private key for the uploaded certificate is not
        present in the keystore by setting the PrivateKeyRequired argument in the upload
        request to true.

        The uploaded certificate has to be linked to a key pair in the keystore. If no
        private key is required for the public key in the certificate and a key pair
        exists in the keystore with a public key equal to the public key in the
        certificate, the uploaded certificate is linked to the key pair identified by
        the supplied key ID by adding a reference from the certificate to the key pair.
        If no private key is required for the public key in the certificate and no key
        pair exists with the public key equal to the public key in the certificate, a
        new key pair with status ok is created with the public key from the certificate,
        and this key pair is linked to the uploaded certificate by adding a reference
        from the certificate to the key pair. If a private key is required for the
        public key in the certificate, and a key pair exists in the keystore with a
        private key that matches the public key in the certificate, the uploaded
        certificate is linked to this keypair by adding a reference from the certificate
        to the key pair. If a private key is required for the public key and no such
        keypair exists in the keystore, the NoMatchingPrivateKey fault shall be produced
        and the certificate shall not be stored in the keystore. If the key pair that
        the certificate shall be linked to does not have status ok, an InvalidKeyID
        fault is produced, and the uploaded certificate is not stored in the keystore.
        If the device cannot process the uploaded certificate, a BadCertificate fault is
        produced and neither the uploaded certificate nor the public key are stored in
        the device’s keystore. The BadCertificate fault shall not be produced based on
        the mere fact that the device’s current time lies outside the interval defined
        by the notBefore and notAfter fields as specified by [RFC 5280], Sect. 4.1 .
        This operation shall not mark the uploaded certificate as trusted.

        If the device does not have not enough storage capacity for storing the
        certificate to be uploaded, the maximum number of certificates reached fault
        shall be produced and no certificate shall be uploaded. If the device does not
        have not enough storage capacity for storing the key pair that eventually has to
        be created, the device shall generate a maximum number of keys reached fault.
        Furthermore the device shall not generate a key pair and no certificate shall be
        stored.
        """
        return self.operator.call(
            "UploadCertificate",
            Certificate=Certificate,
            Alias=Alias,
            KeyAlias=KeyAlias,
            PrivateKeyRequired=PrivateKeyRequired,
        )

    def GetCertificate(self, CertificateID):
        """This operation returns a specific certificate from the device’s keystore.

        Certificates are uniquely identified using certificate IDs. If no certificate is
        stored under the requested certificate ID in the keystore, an InvalidArgVal
        fault is produced. It shall be noted that this command does not return the
        private key that is associated to the public key in the certificate.
        """
        return self.operator.call("GetCertificate", CertificateID=CertificateID)

    def GetAllCertificates(self):
        """This operation returns the IDs of all certificates that are stored in the
        device’s keystore.

        This operation may be used, e.g., if a client lost track of which certificates
        are present on the device. If no certificate is stored in the device’s keystore,
        an empty list is returned.
        """
        return self.operator.call("GetAllCertificates")

    def DeleteCertificate(self, CertificateID):
        """This operation deletes a certificate from the device’s keystore.

        The operation shall not delete the public key that is contained in the
        certificate from the keystore. Certificates are uniquely identified using
        certificate IDs. If no certificate is stored under the requested certificate ID
        in the keystore, an InvalidArgVal fault is produced. If there is a certificate
        under the requested certificate ID stored in the keystore and the certificate
        could not be deleted, a CertificateDeletion fault is produced. If a reference
        exists for the specified certificate, the certificate shall not be deleted and
        the corresponding fault shall be produced. After a certificate has been
        successfully deleted, the device may assign its former ID to other certificates.
        """
        return self.operator.call("DeleteCertificate", CertificateID=CertificateID)

    def CreateCertificationPath(self, CertificateIDs, Alias=None):
        """This operation creates a sequence of certificates that may be used, e.g., for
        certification path validation or for TLS server authentication.

        Certification paths are uniquely identified using certification path IDs.
        Certificates are uniquely identified using certificate IDs. A certification path
        contains a sequence of certificate IDs. If there is a certificate ID in the
        sequence of supplied certificate IDs for which no certificate exists in the
        device’s keystore, the corresponding fault shall be produced and no
        certification path shall be created.

        The signature of each certificate in the certification path except for the last
        one must be verifiable with the public key contained in the next certificate in
        the path. If there is a certificate ID in the request other than the last ID for
        which the corresponding certificate cannot be verified with the public key in
        the certificate identified by the next certificate ID, an
        InvalidCertificateChain fault shall be produced and no certification path shall
        be created.
        """
        return self.operator.call(
            "CreateCertificationPath", CertificateIDs=CertificateIDs, Alias=Alias
        )

    def GetCertificationPath(self, CertificationPathID):
        """This operation returns a specific certification path from the device’s
        keystore.

        Certification paths are uniquely identified using certification path IDs. If no
        certification path is stored under the requested ID in the keystore, an
        InvalidArgVal fault is produced.
        """
        return self.operator.call(
            "GetCertificationPath", CertificationPathID=CertificationPathID
        )

    def GetAllCertificationPaths(self):
        """This operation returns the IDs of all certification paths that are stored in
        the device’s keystore.

        This operation may be used, e.g., if a client lost track of which certificates
        are present on the device. If no certification path is stored on the device, an
        empty list is returned.
        """
        return self.operator.call("GetAllCertificationPaths")

    def SetCertificationPath(self, CertificationPathID, CertificationPath):
        """This operation allows to modify a certification path."""
        return self.operator.call(
            "SetCertificationPath",
            CertificationPathID=CertificationPathID,
            CertificationPath=CertificationPath,
        )

    def DeleteCertificationPath(self, CertificationPathID):
        """This operation deletes a certification path from the device’s keystore.

        This operation shall not delete the certificates that are referenced by the
        certification path. Certification paths are uniquely identified using
        certification path IDs. If no certification path is stored under the requested
        certification path ID in the keystore, an InvalidArgVal fault is produced. If
        there is a certification path under the requested certification path ID stored
        in the keystore and the certification path could not be deleted, a
        CertificationPathDeletion fault is produced. If a reference exists for the
        specified certification path, the certification path shall not be deleted and
        the corresponding fault shall be produced. After a certification path is
        successfully deleted, the device may assign its former ID to other certification
        paths.
        """
        return self.operator.call(
            "DeleteCertificationPath", CertificationPathID=CertificationPathID
        )

    def UploadPassphrase(self, Passphrase, PassphraseAlias=None):
        """This operation uploads a passphrase to the keystore of the device."""
        return self.operator.call(
            "UploadPassphrase", Passphrase=Passphrase, PassphraseAlias=PassphraseAlias
        )

    def GetAllPassphrases(self):
        """This operation returns information about all passphrases that are stored in
        the keystore of the device.

        This operation may be used, e.g., if a client lost track of which passphrases
        are present on the device. If no passphrase is stored on the device, the device
        shall return an empty list.
        """
        return self.operator.call("GetAllPassphrases")

    def DeletePassphrase(self, PassphraseID):
        """This operation deletes a passphrase from the keystore of the device."""
        return self.operator.call("DeletePassphrase", PassphraseID=PassphraseID)

    def UploadCRL(self, Crl, Alias=None, anyParameters=None):
        """This operation uploads a certificate revocation list (CRL) as specified in
        [RFC 5280] to the keystore on the device.

        If the device does not have enough storage space to store the CRL to be
        uploaded, the device shall produce a MaximumNumberOfCRLsReached fault and shall
        not store the supplied CRL. If the device is not able to process the supplied
        CRL, the device shall produce a BadCRL fault and shall not store the supplied
        CRL. If the device does not support the signature algorithm that was used to
        sign the supplied CRL, the device shall produce an UnsupportedSignatureAlgorithm
        fault and shall not store the supplied CRL.
        """
        return self.operator.call(
            "UploadCRL", Crl=Crl, Alias=Alias, anyParameters=anyParameters
        )

    def GetCRL(self, CrlID):
        """This operation returns a specific certificate revocation list (CRL) from the
        keystore on the device.

        Certification revocation lists are uniquely identified using CRLIDs. If no CRL
        is stored under the requested CRLID, the device shall produce a CRLID fault.
        """
        return self.operator.call("GetCRL", CrlID=CrlID)

    def GetAllCRLs(self):
        """This operation returns all certificate revocation lists (CRLs) that are
        stored in the keystore on the device.

        If no certificate revocation list is stored in the device’s keystore, an empty
        list is returned.
        """
        return self.operator.call("GetAllCRLs")

    def DeleteCRL(self, CrlID):
        """This operation deletes a certificate revocation list (CRL) from the keystore
        on the device.

        Certification revocation lists are uniquely identified using CRLIDs. If no CRL
        is stored under the requested CRLID, the device shall produce a CRLID fault. If
        a reference exists for the specified CRL, the device shall produce a
        ReferenceExists fault and shall not delete the CRL. After a CRL has been
        successfully deleted, a device may assign its former ID to other CRLs.
        """
        return self.operator.call("DeleteCRL", CrlID=CrlID)

    def CreateCertPathValidationPolicy(
        self, Parameters, TrustAnchor, Alias=None, anyParameters=None
    ):
        """This operation creates a certification path validation policy.

        Certification path validation policies are uniquely identified using
        certification path validation policy IDs. The device shall generate a new
        certification path validation policy ID for the created certification path
        validation policy. For the certification path validation parameters that are not
        represented in the certPathValidationParameters data type, the device shall use
        the default values specified in Sect. 3. If the device does not have enough
        storage capacity for storing the certification path validation policy to be
        created, the device shall produce a maximum number of certification path
        validation policies reached fault and shall not create a certification path
        validation policy. If there is at least one trust anchor certificate ID in the
        request for which there exists no certificate in the device’s keystore, the
        device shall produce a CertificateID fault and shall not create a certification
        path validation policy. If the device cannot process the supplied certification
        path validation parameters, the device shall produce a
        CertPathValidationParameters fault and shall not create a certification path
        validation policy.
        """
        return self.operator.call(
            "CreateCertPathValidationPolicy",
            Alias=Alias,
            Parameters=Parameters,
            TrustAnchor=TrustAnchor,
            anyParameters=anyParameters,
        )

    def GetCertPathValidationPolicy(self, CertPathValidationPolicyID):
        """This operation returns a certification path validation policy from the
        keystore on the device.

        Certification path validation policies are uniquely identified using
        certification path validation policy IDs. If no certification path validation
        policy is stored under the requested certification path validation policy ID,
        the device shall produce a CertPathValidationPolicyID fault.
        """
        return self.operator.call(
            "GetCertPathValidationPolicy",
            CertPathValidationPolicyID=CertPathValidationPolicyID,
        )

    def GetAllCertPathValidationPolicies(self):
        """This operation returns all certification path validation policies that are
        stored in the keystore on the device.

        If no certification path validation policy is stored in the device’s keystore,
        an empty list is returned.
        """
        return self.operator.call("GetAllCertPathValidationPolicies")

    def SetCertPathValidationPolicy(
        self, CertPathValidationPolicy, CertPathValidationPolicyID=None
    ):
        """This operation allows to modify an existing certification path validation
        policy."""
        return self.operator.call(
            "SetCertPathValidationPolicy",
            CertPathValidationPolicyID=CertPathValidationPolicyID,
            CertPathValidationPolicy=CertPathValidationPolicy,
        )

    def DeleteCertPathValidationPolicy(self, CertPathValidationPolicyID):
        """This operation deletes a certification path validation policy from the
        keystore on the device.

        Certification path validation policies are uniquely identified using
        certification path validation policy IDs. If no certification path validation
        policy is stored under the requested certification path validation policy ID,
        the device shall produce an InvalidCertPathValidationPolicyID fault. If a
        reference exists for the requested certification path validation policy, the
        device shall produce a ReferenceExists fault and shall not delete the
        certification path validation policy. After the certification path validation
        policy has been deleted, the device may assign its former ID to other
        certification path validation policies.
        """
        return self.operator.call(
            "DeleteCertPathValidationPolicy",
            CertPathValidationPolicyID=CertPathValidationPolicyID,
        )
