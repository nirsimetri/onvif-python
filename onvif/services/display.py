# onvif/services/display.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Display(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.1 (June 2011) Split from Core 2.0
        # - DisplayBinding (ver10/display.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/display.wsdl

        definition = ONVIFWSDL.get_definition("display")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Display",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetLayout(self, VideoOutput):
        return self.operator.call("GetLayout", VideoOutput=VideoOutput)

    def SetLayout(self, VideoOutput, Layout):
        return self.operator.call("SetLayout", VideoOutput=VideoOutput, Layout=Layout)

    def GetDisplayOptions(self, VideoOutput):
        return self.operator.call("GetDisplayOptions", VideoOutput=VideoOutput)

    def GetPaneConfigurations(self, VideoOutput):
        return self.operator.call("GetPaneConfigurations", VideoOutput=VideoOutput)

    def GetPaneConfiguration(self, VideoOutput, Pane):
        return self.operator.call(
            "GetPaneConfiguration", VideoOutput=VideoOutput, Pane=Pane
        )

    def SetPaneConfigurations(self, VideoOutput, PaneConfiguration):
        return self.operator.call(
            "SetPaneConfigurations",
            VideoOutput=VideoOutput,
            PaneConfiguration=PaneConfiguration,
        )

    def SetPaneConfiguration(self, VideoOutput, PaneConfiguration):
        return self.operator.call(
            "SetPaneConfiguration",
            VideoOutput=VideoOutput,
            PaneConfiguration=PaneConfiguration,
        )

    def CreatePaneConfiguration(self, VideoOutput, PaneConfiguration):
        return self.operator.call(
            "CreatePaneConfiguration",
            VideoOutput=VideoOutput,
            PaneConfiguration=PaneConfiguration,
        )

    def DeletePaneConfiguration(self, VideoOutput, PaneToken):
        return self.operator.call(
            "DeletePaneConfiguration", VideoOutput=VideoOutput, PaneToken=PaneToken
        )
