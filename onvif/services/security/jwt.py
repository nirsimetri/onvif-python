# onvif/services/security/jwt.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class JWT(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 23.12 (December 2023) Release Notes
        # - JWTBinding (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl

        definition = ONVIFWSDL.get_definition("jwt")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def GetJWTConfiguration(self):
        return self.operator.call("GetJWTConfiguration")

    def SetJWTConfiguration(self, Configuration):
        return self.operator.call("SetJWTConfiguration", Configuration=Configuration)
