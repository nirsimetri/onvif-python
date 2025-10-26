# onvif/services/security/tlsserver.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class TLSServer(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.4 (August 2013) Release Notes
        # - TLSServerBinding (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl

        definition = ONVIFWSDL.get_definition("tlsserver")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def AddServerCertificateAssignment(self, CertificationPathID):
        return self.operator.call(
            "AddServerCertificateAssignment", CertificationPathID=CertificationPathID
        )

    def RemoveServerCertificateAssignment(self, CertificationPathID):
        return self.operator.call(
            "RemoveServerCertificateAssignment", CertificationPathID=CertificationPathID
        )

    def ReplaceServerCertificateAssignment(
        self, OldCertificationPathID, NewCertificationPathID
    ):
        return self.operator.call(
            "ReplaceServerCertificateAssignment",
            OldCertificationPathID=OldCertificationPathID,
            NewCertificationPathID=NewCertificationPathID,
        )

    def GetAssignedServerCertificates(self):
        return self.operator.call("GetAssignedServerCertificates")

    def SetEnabledTLSVersions(self, Versions):
        return self.operator.call("SetEnabledTLSVersions", Versions=Versions)

    def GetEnabledTLSVersions(self):
        return self.operator.call("GetEnabledTLSVersions")

    def SetClientAuthenticationRequired(self, clientAuthenticationRequired):
        return self.operator.call(
            "SetClientAuthenticationRequired",
            clientAuthenticationRequired=clientAuthenticationRequired,
        )

    def GetClientAuthenticationRequired(self):
        return self.operator.call("GetClientAuthenticationRequired")

    def SetCnMapsToUser(self, cnMapsToUser):
        return self.operator.call("SetCnMapsToUser", cnMapsToUser=cnMapsToUser)

    def GetCnMapsToUser(self):
        return self.operator.call("GetCnMapsToUser")

    def AddCertPathValidationPolicyAssignment(self, CertPathValidationPolicyID):
        return self.operator.call(
            "AddCertPathValidationPolicyAssignment",
            CertPathValidationPolicyID=CertPathValidationPolicyID,
        )

    def RemoveCertPathValidationPolicyAssignment(self, CertPathValidationPolicyID):
        return self.operator.call(
            "RemoveCertPathValidationPolicyAssignment",
            CertPathValidationPolicyID=CertPathValidationPolicyID,
        )

    def ReplaceCertPathValidationPolicyAssignment(
        self, OldCertPathValidationPolicyID, NewCertPathValidationPolicyID
    ):
        return self.operator.call(
            "ReplaceCertPathValidationPolicyAssignment",
            OldCertPathValidationPolicyID=OldCertPathValidationPolicyID,
            NewCertPathValidationPolicyID=NewCertPathValidationPolicyID,
        )

    def GetAssignedCertPathValidationPolicies(self):
        return self.operator.call("GetAssignedCertPathValidationPolicies")
