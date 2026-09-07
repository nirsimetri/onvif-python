"""Security (AuthorizationServer) service implementation."""

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class AuthorizationServer(ONVIFService):
    """Security (AuthorizationServer) service client.

    References:
        - First introduced: ONVIF Release 23.12 (December 2023)
        - Binding name: `AuthorizationServerBinding` (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Security.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("authorizationserver")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def GetAuthorizationServerConfigurations(self, Token=None):
        """This operation lists all existing authorization server configurations for the
        device."""
        return self.operator.call("GetAuthorizationServerConfigurations", Token=Token)

    def CreateAuthorizationServerConfiguration(self, Configuration):
        """This operation creates a new authorization server configuration.

        The configuration data shall be created in the device and shall be persistent
        (remain after reboot).
        """
        return self.operator.call(
            "CreateAuthorizationServerConfiguration", Configuration=Configuration
        )

    def SetAuthorizationServerConfiguration(self, Configuration):
        """This operation modifies an existing authorization server configuration."""
        return self.operator.call(
            "SetAuthorizationServerConfiguration", Configuration=Configuration
        )

    def DeleteAuthorizationServerConfiguration(self, Token):
        """This operation deletes the given authorization server configuration and
        configuration change shall always be persistent."""
        return self.operator.call("DeleteAuthorizationServerConfiguration", Token=Token)
