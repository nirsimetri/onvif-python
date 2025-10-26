# onvif/services/uplink.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Uplink(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 18.12 (December 2018) Release Notes
        # - UplinkBinding (ver10/uplink/wsdl/uplink.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/uplink/wsdl/uplink.wsdl

        definition = ONVIFWSDL.get_definition("uplink")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Uplink",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetUplinks(self):
        return self.operator.call("GetUplinks")

    def SetUplink(self, Configuration):
        return self.operator.call("SetUplink", Configuration=Configuration)

    def DeleteUplink(self, RemoteAddress):
        return self.operator.call("DeleteUplink", RemoteAddress=RemoteAddress)
