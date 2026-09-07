"""Security service implementation."""

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-few-public-methods
class AdvancedSecurity(ONVIFService):
    """Security service client.

    References:
        - First introduced: ONVIF Release 2.4 (August 2013)
        - Binding name: `AdvancedSecurityServiceBinding` (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Security.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("advancedsecurity")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="device_service",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the security configuraiton service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")
