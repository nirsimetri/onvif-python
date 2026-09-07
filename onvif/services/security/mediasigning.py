"""Security (MediaSigning) service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class MediaSigning(ONVIFService):
    """Security (MediaSigning) service client.

    References:
        - First introduced: ONVIF Release 24.12 (December 2024)
        - Binding name: `MediaSigningBinding` (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Security.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("mediasigning")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def AddMediaSigningCertificateAssignment(self, CertificationPathID):
        """This operation assigns certification path (certificate chain) to use for
        media signing, replacing the one that is provisioned during factory production.

        The leaf certificate in the chain and its associated private key shall be used
        for signing media as described in the [Media Signing Specification]. This key
        and certificate is referred to as user provisioned key and certificate in that
        specification.

        If this operation is called when there is already a user provisioned
        certification path configured, the existing certification path shall be replaced
        with the new certification path.

        A device shall support this command if the UserMediaSigningKeySupported
        capability is true.
        """
        return self.operator.call(
            "AddMediaSigningCertificateAssignment",
            CertificationPathID=CertificationPathID,
        )

    def RemoveMediaSigningCertificateAssignment(self, CertificationPathID):
        """This operation removes a certificate assignment (including certification
        path) on the device that has been added by AddMediaSigningCertificateAssignment.

        The factory provisioned certification path cannot be removed.

        If media signing on the device is enabled, the device shall produce a
        ReferenceExists fault and shall not remove the certificate assignment.

        A device shall support this command if the UserMediaSigningKeySupported
        capability is true.
        """
        return self.operator.call(
            "RemoveMediaSigningCertificateAssignment",
            CertificationPathID=CertificationPathID,
        )

    def GetAssignedMediaSigningCertificates(self):
        """This operation returns the IDs of the certification paths that are assigned
        for media signing on the device.

        This operation will always return the factory provisioned certification path and
        can additionally return a certification path that has been added by
        AddMediaSigningCertificateAssignment.

        A device shall support this command if the MediaSigningSupported capability is
        true.
        """
        return self.operator.call("GetAssignedMediaSigningCertificates")
