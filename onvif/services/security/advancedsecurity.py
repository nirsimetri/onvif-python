"""Security service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-few-public-methods
class AdvancedSecurity(ONVIFService):
    """Security service client.

    | Property | Details |
    | --- | --- |
    | **First introduced** | ONVIF Release 2.4 (August 2013) |
    | **Binding name** | `AdvancedSecurityServiceBinding` (`ver10/advancedsecurity/wsdl/advancedsecurity.wsdl`) |
    | **Operations** | [advancedsecurity.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl) |
    | **Specification** | [Security.xml](https://developer.onvif.org/pub/specs/branches/development/doc/Security.xml) |
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
