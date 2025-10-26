# onvif/services/imaging.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Imaging(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.1 (June 2011) Split from Core 2.0
        # - ImagingBinding (ver20/imaging/wsdl/imaging.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/imaging/wsdl/imaging.wsdl

        definition = ONVIFWSDL.get_definition("imaging", "ver20")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Imaging",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetImagingSettings(self, VideoSourceToken):
        return self.operator.call(
            "GetImagingSettings", VideoSourceToken=VideoSourceToken
        )

    def SetImagingSettings(
        self, VideoSourceToken, ImagingSettings, ForcePersistence=None
    ):
        return self.operator.call(
            "SetImagingSettings",
            VideoSourceToken=VideoSourceToken,
            ImagingSettings=ImagingSettings,
            ForcePersistence=ForcePersistence,
        )

    def GetOptions(self, VideoSourceToken):
        return self.operator.call("GetOptions", VideoSourceToken=VideoSourceToken)

    def Move(self, VideoSourceToken, Focus):
        return self.operator.call(
            "Move", VideoSourceToken=VideoSourceToken, Focus=Focus
        )

    def Stop(self, VideoSourceToken):
        return self.operator.call("Stop", VideoSourceToken=VideoSourceToken)

    def GetStatus(self, VideoSourceToken):
        return self.operator.call("GetStatus", VideoSourceToken=VideoSourceToken)

    def GetMoveOptions(self, VideoSourceToken):
        return self.operator.call("GetMoveOptions", VideoSourceToken=VideoSourceToken)

    def GetPresets(self, VideoSourceToken):
        return self.operator.call("GetPresets", VideoSourceToken=VideoSourceToken)

    def GetCurrentPreset(self, VideoSourceToken):
        return self.operator.call("GetCurrentPreset", VideoSourceToken=VideoSourceToken)

    def SetCurrentPreset(self, VideoSourceToken, PresetToken):
        return self.operator.call(
            "SetCurrentPreset",
            VideoSourceToken=VideoSourceToken,
            PresetToken=PresetToken,
        )
