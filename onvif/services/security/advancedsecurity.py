"""Security service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils.service import ONVIFService
from onvif.utils.wsdl import ONVIFWSDL


class AdvancedSecurity(ONVIFService):
    """Security service client.

    | Property | Details |
    | -------- | ------- |
    | **First introduced** | ONVIF Release 2.4 (August 2013) |
    | **Binding name** | `AdvancedSecurityServiceBinding` (`ver10/advancedsecurity/wsdl/advancedsecurity.wsdl`) |
    | **Operations** | [advancedsecurity.wsdl](https://www.onvif.org/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl) |
    | **Spec** | [Security](https://www.onvif.org/specs/srv/security/ONVIF-Security-Service-Spec.pdf) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("advancedsecurity")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Security",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the security configuration service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")
