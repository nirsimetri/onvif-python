"""Security (JWT) service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils.service import ONVIFService
from onvif.utils.wsdl import ONVIFWSDL


class JWT(ONVIFService):
    """
    <!-- md:version 0.0.1 -->
    <!-- md:onvif_version 23.12 https://www.onvif.org/profiles/specifications/specification-history/december-2023 -->

    Security (JWT) service client.

    | Property | Details |
    | -------- | ------- |
    | **First introduced** | ONVIF 23.12 (December 2023) |
    | **Binding name** | `JWTBinding` (`ver10/advancedsecurity/wsdl/advancedsecurity.wsdl`) |
    | **Operations** | [advancedsecurity.wsdl](https://www.onvif.org/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl) |
    | **Spec** | [Security](https://www.onvif.org/specs/srv/security/ONVIF-Security-Service-Spec.pdf) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("jwt")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def GetJWTConfiguration(self):
        """This operation returns the parameters of the JWT authorization used by the
        device.
        """
        return self.operator.call("GetJWTConfiguration")

    def SetJWTConfiguration(self, Configuration):
        """This operation sets the parameters of the JWT authorization used by the
        device.
        """
        return self.operator.call("SetJWTConfiguration", Configuration=Configuration)
