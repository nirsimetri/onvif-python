"""Security (TLSServer) service implementation."""

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class TLSServer(ONVIFService):
    """Security (TLSServer) service client.

    References:
        - First introduced: ONVIF Release 2.4 (August 2013)
        - Binding name: `TLSServerBinding` (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Security.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("tlsserver")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def AddServerCertificateAssignment(self, CertificationPathID):
        """This operation assigns a key pair and certificate along with a certification
        path (certificate chain) to the TLS server on the device.

        The TLS server shall use this information for key exchange during the TLS
        handshake, particularly for constructing server certificate messages as
        specified in RFC 4346 and RFC 2246.

        Certification paths are identified by their certification path IDs in the
        keystore. The first certificate in the certification path must be the TLS server
        certificate. Since each certificate has exactly one associated key pair, a
        reference to the key pair that is associated with the server certificate is not
        supplied explicitly. Devices shall obtain the private key or results of
        operations under the private key by suitable internal interaction with the
        keystore.

        If a device chooses to perform a TLS key exchange based on the supplied
        certification path, it shall use the key pair that is associated with the server
        certificate for key exchange and transmit the certification path to TLS clients
        as-is, i.e., the device shall not check conformance of the certification path to
        RFC 4346 norRFC 2246. In order to use the server certificate during the TLS
        handshake, the corresponding private key is required. Therefore, if the key pair
        that is associated with the server certificate, i.e., the first certificate in
        the certification path, does not have an associated private key, the
        NoPrivateKey fault is produced and the certification path is not associated to
        the TLS server.

        A TLS server may present different certification paths to different clients
        during the TLS handshake instead of presenting the same certification path to
        all clients. Therefore more than one certification path may be assigned to the
        TLS server.

        If the maximum number of certification paths that may be assigned to the TLS
        server simultaneously is reached, the device shall generate a
        MaximumNumberOfCertificationPathsReached fault and the requested certification
        path shall not be assigned to the TLS server.
        """
        return self.operator.call(
            "AddServerCertificateAssignment", CertificationPathID=CertificationPathID
        )

    def RemoveServerCertificateAssignment(self, CertificationPathID):
        """This operation removes a key pair and certificate assignment (including
        certification path) to the TLS server on the device.

        Certification paths are identified using certification path IDs. If the supplied
        certification path ID is not associated to the TLS server, an InvalidArgVal
        fault is produced.
        """
        return self.operator.call(
            "RemoveServerCertificateAssignment", CertificationPathID=CertificationPathID
        )

    def ReplaceServerCertificateAssignment(
        self, OldCertificationPathID, NewCertificationPathID
    ):
        """This operation replaces an existing key pair and certificate assignment to
        the TLS server on the device by a new key pair and certificate assignment
        (including certification paths).

        After the replacement, the TLS server shall use the new certificate and
        certification path exactly in those cases in which it would have used the old
        certificate and certification path. Therefore, especially in the case that
        several server certificates are assigned to the TLS server, clients that wish to
        replace an old certificate assignment by a new assignment should use this
        operation instead of a combination of the Add TLS Server Certificate Assignment
        and the Remove TLS Server Certificate Assignment operations.

        Certification paths are identified using certification path IDs. If the supplied
        old certification path ID is not associated to the TLS server, or no
        certification path exists under the new certification path ID, the corresponding
        InvalidArgVal faults are produced and the associations are unchanged. The first
        certificate in the new certification path must be the TLS server certificate.

        Since each certificate has exactly one associated key pair, a reference to the
        key pair that is associated with the new server certificate is not supplied
        explicitly. Devices shall obtain the private key or results of operations under
        the private key by suitable internal interaction with the keystore.

        If a device chooses to perform a TLS key exchange based on the new certification
        path, it shall use the key pair that is associated with the server certificate
        for key exchange and transmit the certification path to TLS clients as-is, i.e.,
        the device shall not check conformance of the certification path to RFC 4346
        norRFC 2246. In order to use the server certificate during the TLS handshake,
        the corresponding private key is required. Therefore, if the key pair that is
        associated with the server certificate, i.e., the first certificate in the
        certification path, does not have an associated private key, the NoPrivateKey
        fault is produced and the certification path is not associated to the TLS
        server.
        """
        return self.operator.call(
            "ReplaceServerCertificateAssignment",
            OldCertificationPathID=OldCertificationPathID,
            NewCertificationPathID=NewCertificationPathID,
        )

    def GetAssignedServerCertificates(self):
        """This operation returns the IDs of all key pairs and certificates (including
        certification paths) that are assigned to the TLS server on the device.

        This operation may be used, e.g., if a client lost track of the certification
        path assignments on the device. If no certification path is assigned to the TLS
        server, an empty list is returned.
        """
        return self.operator.call("GetAssignedServerCertificates")

    def SetEnabledTLSVersions(self, Versions):
        """This operation sets the version(s) of TLS which the device shall use.

        Valid values are taken from the TLSServerSupported capability. A client
        initiates a TLS session by sending a ClientHello with the hightest TLS version
        it supports. This suggests to the server that the client can accept any TLS
        version up to and including that version.

        The server then chooses the TLS version to use. This is generally the highest
        TLS version the server supports that is within the range of the client. For
        example, if a ClientHello indicates TLS version 1.1, the server can proceed with
        TLS 1.0 or TLS 1.1.

        In the event that an ONVIF installation wishes to disable certain version(s) of
        TLS, it may do so with this operation. For example, to disable TLS 1.0 on a
        device signaling support for TLS versions 1.0, 1.1, and 1.2, the enabled version
        list may be set to "1.1 1.2", omitting 1.0. If a client then attempts to connect
        with a ClientHello containing TLS 1.0, the server shall send a
        "protocol_version" alert message and close the connection. This handshake
        indicates to the client that TLS 1.0 is not supported by the server. The client
        must try again with a higher TLS version suggestion.

        An empty list is not permitted. Disabling all versions of TLS is not the intent
        of this operation. See AddServerCertificateAssignment and
        RemoveServerCertificateAssignment.
        """
        return self.operator.call("SetEnabledTLSVersions", Versions=Versions)

    def GetEnabledTLSVersions(self):
        """This operation retrieves the version(s) of TLS which are currently enabled on
        the device."""
        return self.operator.call("GetEnabledTLSVersions")

    def SetClientAuthenticationRequired(self, clientAuthenticationRequired):
        """This operation activates or deactivates TLS client authentication for the TLS
        server on the device.

        The TLS server on the device shall require client authentication if and only if
        clientAuthenticationRequired is set to true. If TLS client authentication is
        requested to be enabled and no certification path validation policy is assigned
        to the TLS server, the device shall return an
        EnablingTLSClientAuthenticationFailed fault and shall not enable TLS client
        authentication. The device shall execute this command regardless of the TLS
        enabled/disabled state configured in the ONVIF Device Management Service.
        """
        return self.operator.call(
            "SetClientAuthenticationRequired",
            clientAuthenticationRequired=clientAuthenticationRequired,
        )

    def GetClientAuthenticationRequired(self):
        """This operation returns whether TLS client authentication is active."""
        return self.operator.call("GetClientAuthenticationRequired")

    def SetCnMapsToUser(self, cnMapsToUser):
        """This operation enables or disables mapping of the Common Name present in the
        TLS client certificate to an existing user name in the device.

        The TLS server on the device shall perform mapping if parameter
        clientAuthenticationRequired is set to true.
        """
        return self.operator.call("SetCnMapsToUser", cnMapsToUser=cnMapsToUser)

    def GetCnMapsToUser(self):
        """This operation returns whether the Common Name Mapping to User is enabled."""
        return self.operator.call("GetCnMapsToUser")

    def AddCertPathValidationPolicyAssignment(self, CertPathValidationPolicyID):
        """This operation assigns a certification path validation policy to the TLS
        server on the device.

        The TLS server shall enforce the policy when authenticating TLS clients and
        consider a client authentic if and only if the algorithm returns valid. If no
        certification path validation policy is stored under the requested
        CertPathValidationPolicyID, the device shall produce a
        CertPathValidationPolicyID fault. A TLS server may use different certification
        path validation policies to authenticate clients. Therefore more than one
        certification path validation policy may be assigned to the TLS server. If the
        maximum number of certification path validation policies that may be assigned to
        the TLS server simultaneously is reached, the device shall produce a
        MaximumNumberOfTLSCertPathValidationPoliciesReached fault and shall not assign
        the requested certification path validation policy to the TLS server.
        """
        return self.operator.call(
            "AddCertPathValidationPolicyAssignment",
            CertPathValidationPolicyID=CertPathValidationPolicyID,
        )

    def RemoveCertPathValidationPolicyAssignment(self, CertPathValidationPolicyID):
        """This operation removes a certification path validation policy assignment from
        the TLS server on the device.

        If the certification path validation policy identified by the requested
        CertPathValidationPolicyID is not associated to the TLS server, the device shall
        produce a CertPathValidationPolicy fault.
        """
        return self.operator.call(
            "RemoveCertPathValidationPolicyAssignment",
            CertPathValidationPolicyID=CertPathValidationPolicyID,
        )

    def ReplaceCertPathValidationPolicyAssignment(
        self, OldCertPathValidationPolicyID, NewCertPathValidationPolicyID
    ):
        """This operation replaces a certification path validation policy assignment to
        the TLS server on the device with another certification path validation policy
        assignment.

        If the certification path validation policy identified by the requested
        OldCertPathValidationPolicyID is not associated to the TLS server, the device
        shall produce an OldCertPathValidationPolicyID fault and shall not associate the
        certification path validation policy identified by the
        NewCertPathValidationPolicyID to the TLS server. If no certification path
        validation policy exists under the requested NewCertPathValidationPolicyID in
        the device’s keystore, the device shall produce a NewCertPathValidationPolicyID
        fault and shall not remove the association of the old certification path
        validation policy to the TLS server.
        """
        return self.operator.call(
            "ReplaceCertPathValidationPolicyAssignment",
            OldCertPathValidationPolicyID=OldCertPathValidationPolicyID,
            NewCertPathValidationPolicyID=NewCertPathValidationPolicyID,
        )

    def GetAssignedCertPathValidationPolicies(self):
        """This operation returns the IDs of all certification path validation policies
        that are assigned to the TLS server on the device."""
        return self.operator.call("GetAssignedCertPathValidationPolicies")
