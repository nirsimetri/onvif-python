# onvif/services/provisioning.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Provisioning(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 16.12 (December 2016) Release Notes
        # - ProvisioningBinding (ver10/provisioning/wsdl/provisioning.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/provisioning/wsdl/provisioning.wsdl

        definition = ONVIFWSDL.get_definition("provisioning")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Provisioning",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def PanMove(self, VideoSource, Direction, Timeout=None):
        return self.operator.call(
            "PanMove", VideoSource=VideoSource, Direction=Direction, Timeout=Timeout
        )

    def TiltMove(self, VideoSource, Direction, Timeout=None):
        return self.operator.call(
            "TiltMove", VideoSource=VideoSource, Direction=Direction, Timeout=Timeout
        )

    def ZoomMove(self, VideoSource, Direction, Timeout=None):
        return self.operator.call(
            "ZoomMove", VideoSource=VideoSource, Direction=Direction, Timeout=Timeout
        )

    def RollMove(self, VideoSource, Direction, Timeout=None):
        return self.operator.call(
            "RollMove", VideoSource=VideoSource, Direction=Direction, Timeout=Timeout
        )

    def FocusMove(self, VideoSource, Direction, Timeout=None):
        return self.operator.call(
            "FocusMove", VideoSource=VideoSource, Direction=Direction, Timeout=Timeout
        )

    def Stop(self, VideoSource):
        return self.operator.call("Stop", VideoSource=VideoSource)

    def GetUsage(self, VideoSource):
        return self.operator.call("GetUsage", VideoSource=VideoSource)
