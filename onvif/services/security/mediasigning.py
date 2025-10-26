# onvif/services/security/mediasigning.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class MediaSigning(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 24.12 (December 2024) Release Notes
        # - MediaSigningBinding (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl

        definition = ONVIFWSDL.get_definition("mediasigning")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def AddMediaSigningCertificateAssignment(self, CertificationPathID):
        return self.operator.call(
            "AddMediaSigningCertificateAssignment",
            CertificationPathID=CertificationPathID,
        )

    def RemoveMediaSigningCertificateAssignment(self, CertificationPathID):
        return self.operator.call(
            "RemoveMediaSigningCertificateAssignment",
            CertificationPathID=CertificationPathID,
        )

    def GetAssignedMediaSigningCertificates(self):
        return self.operator.call("GetAssignedMediaSigningCertificates")
