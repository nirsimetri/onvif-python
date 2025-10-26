# onvif/services/ptz.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class PTZ(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.1 (June 2011) Split from Core 2.0
        # - PTZBinding (ver20/ptz/wsdl/ptz.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/ptz/wsdl/ptz.wsdl

        definition = ONVIFWSDL.get_definition("ptz", "ver20")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="PTZ",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetConfigurations(self):
        return self.operator.call("GetConfigurations")

    def GetPresets(self, ProfileToken):
        return self.operator.call("GetPresets", ProfileToken=ProfileToken)

    def SetPreset(self, ProfileToken, PresetName=None, PresetToken=None):
        return self.operator.call(
            "SetPreset",
            ProfileToken=ProfileToken,
            PresetName=PresetName,
            PresetToken=PresetToken,
        )

    def RemovePreset(self, ProfileToken, PresetToken):
        return self.operator.call(
            "RemovePreset", ProfileToken=ProfileToken, PresetToken=PresetToken
        )

    def GotoPreset(self, ProfileToken, PresetToken, Speed=None):
        return self.operator.call(
            "GotoPreset",
            ProfileToken=ProfileToken,
            PresetToken=PresetToken,
            Speed=Speed,
        )

    def GetStatus(self, ProfileToken):
        return self.operator.call("GetStatus", ProfileToken=ProfileToken)

    def GetConfiguration(self, PTZConfigurationToken):
        return self.operator.call(
            "GetConfiguration", PTZConfigurationToken=PTZConfigurationToken
        )

    def GetNodes(self):
        return self.operator.call("GetNodes")

    def GetNode(self, NodeToken):
        return self.operator.call("GetNode", NodeToken=NodeToken)

    def SetConfiguration(self, PTZConfiguration, ForcePersistence):
        return self.operator.call(
            "SetConfiguration",
            PTZConfiguration=PTZConfiguration,
            ForcePersistence=ForcePersistence,
        )

    def GetConfigurationOptions(self, ConfigurationToken):
        return self.operator.call(
            "GetConfigurationOptions", ConfigurationToken=ConfigurationToken
        )

    def GotoHomePosition(self, ProfileToken, Speed=None):
        return self.operator.call(
            "GotoHomePosition", ProfileToken=ProfileToken, Speed=Speed
        )

    def SetHomePosition(self, ProfileToken):
        return self.operator.call("SetHomePosition", ProfileToken=ProfileToken)

    def ContinuousMove(self, ProfileToken, Velocity, Timeout=None):
        return self.operator.call(
            "ContinuousMove",
            ProfileToken=ProfileToken,
            Velocity=Velocity,
            Timeout=Timeout,
        )

    def RelativeMove(self, ProfileToken, Translation, Speed=None):
        return self.operator.call(
            "RelativeMove",
            ProfileToken=ProfileToken,
            Translation=Translation,
            Speed=Speed,
        )

    def SendAuxiliaryCommand(self, ProfileToken, AuxiliaryData):
        return self.operator.call(
            "SendAuxiliaryCommand",
            ProfileToken=ProfileToken,
            AuxiliaryData=AuxiliaryData,
        )

    def AbsoluteMove(self, ProfileToken, Position, Speed=None):
        return self.operator.call(
            "AbsoluteMove", ProfileToken=ProfileToken, Position=Position, Speed=Speed
        )

    def GeoMove(
        self, ProfileToken, Target, Speed=None, AreaHeight=None, AreaWidth=None
    ):
        return self.operator.call(
            "GeoMove",
            ProfileToken=ProfileToken,
            Target=Target,
            Speed=Speed,
            AreaHeight=AreaHeight,
            AreaWidth=AreaWidth,
        )

    def Stop(self, ProfileToken, PanTilt=None, Zoom=None):
        return self.operator.call(
            "Stop", ProfileToken=ProfileToken, PanTilt=PanTilt, Zoom=Zoom
        )

    def GetPresetTours(self, ProfileToken):
        return self.operator.call("GetPresetTours", ProfileToken=ProfileToken)

    def GetPresetTour(self, ProfileToken, PresetTourToken):
        return self.operator.call(
            "GetPresetTour", ProfileToken=ProfileToken, PresetTourToken=PresetTourToken
        )

    def GetPresetTourOptions(self, ProfileToken, PresetTourToken=None):
        return self.operator.call(
            "GetPresetTourOptions",
            ProfileToken=ProfileToken,
            PresetTourToken=PresetTourToken,
        )

    def CreatePresetTour(self, ProfileToken):
        return self.operator.call("CreatePresetTour", ProfileToken=ProfileToken)

    def ModifyPresetTour(self, ProfileToken, PresetTour):
        return self.operator.call(
            "ModifyPresetTour", ProfileToken=ProfileToken, PresetTour=PresetTour
        )

    def OperatePresetTour(self, ProfileToken, PresetTourToken, Operation):
        return self.operator.call(
            "OperatePresetTour",
            ProfileToken=ProfileToken,
            PresetTourToken=PresetTourToken,
            Operation=Operation,
        )

    def RemovePresetTour(self, ProfileToken, PresetTourToken):
        return self.operator.call(
            "RemovePresetTour",
            ProfileToken=ProfileToken,
            PresetTourToken=PresetTourToken,
        )

    def GetCompatibleConfigurations(self, ProfileToken):
        return self.operator.call(
            "GetCompatibleConfigurations", ProfileToken=ProfileToken
        )

    def MoveAndStartTracking(
        self,
        ProfileToken,
        ObjectID,
        PresetToken=None,
        GeoLocation=None,
        TargetPosition=None,
        Speed=None,
    ):
        return self.operator.call(
            "MoveAndStartTracking",
            ProfileToken=ProfileToken,
            PresetToken=PresetToken,
            GeoLocation=GeoLocation,
            TargetPosition=TargetPosition,
            Speed=Speed,
            ObjectID=ObjectID,
        )
