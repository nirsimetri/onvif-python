# onvif/services/security/authorizationserver.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class AuthorizationServer(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 23.12 (December 2023) Release Notes
        # - AuthorizationServerBinding (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl

        definition = ONVIFWSDL.get_definition("authorizationserver")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def GetAuthorizationServerConfigurations(self, Token=None):
        return self.operator.call("GetAuthorizationServerConfigurations", Token=Token)

    def CreateAuthorizationServerConfiguration(self, Configuration):
        return self.operator.call(
            "CreateAuthorizationServerConfiguration", Configuration=Configuration
        )

    def SetAuthorizationServerConfiguration(self, Configuration):
        return self.operator.call(
            "SetAuthorizationServerConfiguration", Configuration=Configuration
        )

    def DeleteAuthorizationServerConfiguration(self, Token):
        return self.operator.call("DeleteAuthorizationServerConfiguration", Token=Token)
