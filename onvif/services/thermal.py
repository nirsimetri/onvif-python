# onvif/services/thermal.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Thermal(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 16.06 (June 2016) Release Notes
        # - ThermalBinding (ver10/thermal/wsdl/thermal.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/thermal/wsdl/thermal.wsdl

        definition = ONVIFWSDL.get_definition("thermal")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Thermal",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetConfigurationOptions(self, VideoSourceToken):
        return self.operator.call(
            "GetConfigurationOptions", VideoSourceToken=VideoSourceToken
        )

    def GetConfiguration(self, VideoSourceToken):
        return self.operator.call("GetConfiguration", VideoSourceToken=VideoSourceToken)

    def GetConfigurations(self):
        return self.operator.call("GetConfigurations")

    def SetConfiguration(self, VideoSourceToken, Configuration):
        return self.operator.call(
            "SetConfiguration",
            VideoSourceToken=VideoSourceToken,
            Configuration=Configuration,
        )

    def GetRadiometryConfigurationOptions(self, VideoSourceToken):
        return self.operator.call(
            "GetRadiometryConfigurationOptions", VideoSourceToken=VideoSourceToken
        )

    def GetRadiometryConfiguration(self, VideoSourceToken):
        return self.operator.call(
            "GetRadiometryConfiguration", VideoSourceToken=VideoSourceToken
        )

    def SetRadiometryConfiguration(self, VideoSourceToken, Configuration):
        return self.operator.call(
            "SetRadiometryConfiguration",
            VideoSourceToken=VideoSourceToken,
            Configuration=Configuration,
        )
