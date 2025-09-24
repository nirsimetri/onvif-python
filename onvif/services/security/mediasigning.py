# onvif/services/security/mediasigning.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL


class MediaSigning:
    def __init__(self, xaddr=None, **kwargs):
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
