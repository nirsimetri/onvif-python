# onvif/services/media2.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Media2(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.61 (December 2015) Release Notes
        # - Media2Binding (ver20/media/wsdl/media.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/media/wsdl/media.wsdl

        definition = ONVIFWSDL.get_definition("media2", "ver20")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Media2",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def CreateProfile(self, Name, Configuration=None):
        return self.operator.call(
            "CreateProfile", Name=Name, Configuration=Configuration
        )

    def GetProfiles(self, Token=None, Type=None):
        return self.operator.call("GetProfiles", Token=Token, Type=Type)

    def AddConfiguration(self, ProfileToken, Name=None, Configuration=None):
        return self.operator.call(
            "AddConfiguration",
            ProfileToken=ProfileToken,
            Name=Name,
            Configuration=Configuration,
        )

    def RemoveConfiguration(self, ProfileToken, Configuration):
        return self.operator.call(
            "RemoveConfiguration",
            ProfileToken=ProfileToken,
            Configuration=Configuration,
        )

    def DeleteProfile(self, Token):
        return self.operator.call("DeleteProfile", Token=Token)

    def GetVideoSourceConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        return self.operator.call(
            "GetVideoSourceConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetVideoEncoderConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        return self.operator.call(
            "GetVideoEncoderConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioSourceConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        return self.operator.call(
            "GetAudioSourceConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioEncoderConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        return self.operator.call(
            "GetAudioEncoderConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAnalyticsConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        return self.operator.call(
            "GetAnalyticsConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetMetadataConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        return self.operator.call(
            "GetMetadataConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioOutputConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        return self.operator.call(
            "GetAudioOutputConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioDecoderConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        return self.operator.call(
            "GetAudioDecoderConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def SetVideoSourceConfiguration(self, Configuration):
        return self.operator.call(
            "SetVideoSourceConfiguration", Configuration=Configuration
        )

    def SetVideoEncoderConfiguration(self, Configuration):
        return self.operator.call(
            "SetVideoEncoderConfiguration", Configuration=Configuration
        )

    def SetAudioSourceConfiguration(self, Configuration):
        return self.operator.call(
            "SetAudioSourceConfiguration", Configuration=Configuration
        )

    def SetAudioEncoderConfiguration(self, Configuration):
        return self.operator.call(
            "SetAudioEncoderConfiguration", Configuration=Configuration
        )

    def SetMetadataConfiguration(self, Configuration):
        return self.operator.call(
            "SetMetadataConfiguration", Configuration=Configuration
        )

    def SetAudioOutputConfiguration(self, Configuration):
        return self.operator.call(
            "SetAudioOutputConfiguration", Configuration=Configuration
        )

    def SetAudioDecoderConfiguration(self, Configuration):
        return self.operator.call(
            "SetAudioDecoderConfiguration", Configuration=Configuration
        )

    def SetEQPreset(self, Configuration):
        return self.operator.call("SetEQPreset", Configuration=Configuration)

    def GetVideoSourceConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        return self.operator.call(
            "GetVideoSourceConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetVideoEncoderConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        return self.operator.call(
            "GetVideoEncoderConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioSourceConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        return self.operator.call(
            "GetAudioSourceConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioEncoderConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        return self.operator.call(
            "GetAudioEncoderConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetMetadataConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        return self.operator.call(
            "GetMetadataConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioOutputConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        return self.operator.call(
            "GetAudioOutputConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioDecoderConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        return self.operator.call(
            "GetAudioDecoderConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetVideoEncoderInstances(self, ConfigurationToken):
        return self.operator.call(
            "GetVideoEncoderInstances", ConfigurationToken=ConfigurationToken
        )

    def GetStreamUri(self, Protocol, ProfileToken):
        return self.operator.call(
            "GetStreamUri", Protocol=Protocol, ProfileToken=ProfileToken
        )

    def StartMulticastStreaming(self, ProfileToken):
        return self.operator.call("StartMulticastStreaming", ProfileToken=ProfileToken)

    def StopMulticastStreaming(self, ProfileToken):
        return self.operator.call("StopMulticastStreaming", ProfileToken=ProfileToken)

    def SetSynchronizationPoint(self, ProfileToken):
        return self.operator.call("SetSynchronizationPoint", ProfileToken=ProfileToken)

    def GetSnapshotUri(self, ProfileToken):
        return self.operator.call("GetSnapshotUri", ProfileToken=ProfileToken)

    def GetVideoSourceModes(self, VideoSourceToken):
        return self.operator.call(
            "GetVideoSourceModes", VideoSourceToken=VideoSourceToken
        )

    def SetVideoSourceMode(self, VideoSourceToken, VideoSourceModeToken):
        return self.operator.call(
            "SetVideoSourceMode",
            VideoSourceToken=VideoSourceToken,
            VideoSourceModeToken=VideoSourceModeToken,
        )

    def GetOSDs(self, OSDToken=None, ConfigurationToken=None):
        return self.operator.call(
            "GetOSDs", OSDToken=OSDToken, ConfigurationToken=ConfigurationToken
        )

    def GetOSDOptions(self, ConfigurationToken):
        return self.operator.call(
            "GetOSDOptions", ConfigurationToken=ConfigurationToken
        )

    def SetOSD(self, OSD):
        return self.operator.call("SetOSD", OSD=OSD)

    def CreateOSD(self, OSD):
        return self.operator.call("CreateOSD", OSD=OSD)

    def DeleteOSD(self, OSDToken):
        return self.operator.call("DeleteOSD", OSDToken=OSDToken)

    def GetMasks(self, Token=None, ConfigurationToken=None):
        return self.operator.call(
            "GetMasks", Token=Token, ConfigurationToken=ConfigurationToken
        )

    def GetMaskOptions(self, ConfigurationToken):
        return self.operator.call(
            "GetMaskOptions", ConfigurationToken=ConfigurationToken
        )

    def SetMask(self, Mask):
        return self.operator.call("SetMask", Mask=Mask)

    def CreateMask(self, Mask):
        return self.operator.call("CreateMask", Mask=Mask)

    def DeleteMask(self, Token):
        return self.operator.call("DeleteMask", Token=Token)

    def GetWebRTCConfigurations(self):
        return self.operator.call("GetWebRTCConfigurations")

    def SetWebRTCConfigurations(self, WebRTCConfiguration=None):
        return self.operator.call(
            "SetWebRTCConfigurations", WebRTCConfiguration=WebRTCConfiguration
        )

    def GetAudioClips(self, Token=None):
        return self.operator.call("GetAudioClips", Token=Token)

    def AddAudioClip(self, Configuration, Token=None):
        return self.operator.call(
            "AddAudioClip", Token=Token, Configuration=Configuration
        )

    def SetAudioClip(self, Token, Configuration):
        return self.operator.call(
            "SetAudioClip", Token=Token, Configuration=Configuration
        )

    def DeleteAudioClip(self, Token):
        return self.operator.call("DeleteAudioClip", Token=Token)

    def PlayAudioClip(self, Token, Play, AudioOutputToken=None, RepeatCycles=None):
        return self.operator.call(
            "PlayAudioClip",
            Token=Token,
            AudioOutputToken=AudioOutputToken,
            Play=Play,
            RepeatCycles=RepeatCycles,
        )

    def GetPlayingAudioClips(self):
        return self.operator.call("GetPlayingAudioClips")

    def GetMulticastAudioDecoderConfigurationOptions(self, ConfigurationToken=None):
        return self.operator.call(
            "GetMulticastAudioDecoderConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
        )

    def GetMulticastAudioDecoderConfigurations(self, ConfigurationToken=None):
        return self.operator.call(
            "GetMulticastAudioDecoderConfigurations",
            ConfigurationToken=ConfigurationToken,
        )

    def SetMulticastAudioDecoderConfiguration(self, Configuration):
        return self.operator.call(
            "SetMulticastAudioDecoderConfiguration", Configuration=Configuration
        )
