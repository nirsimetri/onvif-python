"""Security (JWT) service implementation."""

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class JWT(ONVIFService):
    """Security (JWT) service client.

    References:
        - First introduced: ONVIF Release 23.12 (December 2023)
        - Binding name: `JWTBinding` (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Security.xml
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
        device."""
        return self.operator.call("GetJWTConfiguration")

    def SetJWTConfiguration(self, Configuration):
        """This operation sets the parameters of the JWT authorization used by the
        device."""
        return self.operator.call("SetJWTConfiguration", Configuration=Configuration)
