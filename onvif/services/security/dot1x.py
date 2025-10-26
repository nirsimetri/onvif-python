# onvif/services/security/dot1x.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class Dot1X(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 16.06 (June 2016) Release Notes
        # - Dot1XBinding (ver10/advancedsecurity/wsdl/advancedsecurity.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/advancedsecurity/wsdl/advancedsecurity.wsdl

        definition = ONVIFWSDL.get_definition("dot1x")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def AddDot1XConfiguration(self, Dot1XConfiguration):
        return self.operator.call(
            "AddDot1XConfiguration", Dot1XConfiguration=Dot1XConfiguration
        )

    def GetAllDot1XConfigurations(self):
        return self.operator.call("GetAllDot1XConfigurations")

    def GetDot1XConfiguration(self, Dot1XID):
        return self.operator.call("GetDot1XConfiguration", Dot1XID=Dot1XID)

    def DeleteDot1XConfiguration(self, Dot1XID):
        return self.operator.call("DeleteDot1XConfiguration", Dot1XID=Dot1XID)

    def SetNetworkInterfaceDot1XConfiguration(self, token, Dot1XID):
        return self.operator.call(
            "SetNetworkInterfaceDot1XConfiguration", token=token, Dot1XID=Dot1XID
        )

    def GetNetworkInterfaceDot1XConfiguration(self, token):
        return self.operator.call("GetNetworkInterfaceDot1XConfiguration", token=token)

    def DeleteNetworkInterfaceDot1XConfiguration(self, token):
        return self.operator.call(
            "DeleteNetworkInterfaceDot1XConfiguration", token=token
        )
