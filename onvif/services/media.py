# onvif/services/media.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Media(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.1 (June 2011) Split from Core 2.0
        # - MediaBinding (ver10/media/wsdl/media.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/media/wsdl/media.wsdl

        definition = ONVIFWSDL.get_definition("media")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Media",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetVideoSources(self):
        return self.operator.call("GetVideoSources")

    def GetAudioSources(self):
        return self.operator.call("GetAudioSources")

    def GetAudioOutputs(self):
        return self.operator.call("GetAudioOutputs")

    def CreateProfile(self, Name, Token=None):
        return self.operator.call("CreateProfile", Name=Name, Token=Token)

    def GetProfile(self, ProfileToken):
        return self.operator.call("GetProfile", ProfileToken=ProfileToken)

    def GetProfiles(self):
        return self.operator.call("GetProfiles")

    def AddVideoEncoderConfiguration(self, ProfileToken, ConfigurationToken):
        return self.operator.call(
            "AddVideoEncoderConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddVideoSourceConfiguration(self, ProfileToken, ConfigurationToken):
        return self.operator.call(
            "AddVideoSourceConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddAudioEncoderConfiguration(self, ProfileToken, ConfigurationToken):
        return self.operator.call(
            "AddAudioEncoderConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddAudioSourceConfiguration(self, ProfileToken, ConfigurationToken):
        return self.operator.call(
            "AddAudioSourceConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddPTZConfiguration(self, ProfileToken, ConfigurationToken):
        return self.operator.call(
            "AddPTZConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddVideoAnalyticsConfiguration(self, ProfileToken, ConfigurationToken):
        return self.operator.call(
            "AddVideoAnalyticsConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddMetadataConfiguration(self, ProfileToken, ConfigurationToken):
        return self.operator.call(
            "AddMetadataConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddAudioOutputConfiguration(self, ProfileToken, ConfigurationToken):
        return self.operator.call(
            "AddAudioOutputConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddAudioDecoderConfiguration(self, ProfileToken, ConfigurationToken):
        return self.operator.call(
            "AddAudioDecoderConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def RemoveVideoEncoderConfiguration(self, ProfileToken):
        return self.operator.call(
            "RemoveVideoEncoderConfiguration", ProfileToken=ProfileToken
        )

    def RemoveVideoSourceConfiguration(self, ProfileToken):
        return self.operator.call(
            "RemoveVideoSourceConfiguration", ProfileToken=ProfileToken
        )

    def RemoveAudioEncoderConfiguration(self, ProfileToken):
        return self.operator.call(
            "RemoveAudioEncoderConfiguration", ProfileToken=ProfileToken
        )

    def RemoveAudioSourceConfiguration(self, ProfileToken):
        return self.operator.call(
            "RemoveAudioSourceConfiguration", ProfileToken=ProfileToken
        )

    def RemovePTZConfiguration(self, ProfileToken):
        return self.operator.call("RemovePTZConfiguration", ProfileToken=ProfileToken)

    def RemoveVideoAnalyticsConfiguration(self, ProfileToken):
        return self.operator.call(
            "RemoveVideoAnalyticsConfiguration", ProfileToken=ProfileToken
        )

    def RemoveMetadataConfiguration(self, ProfileToken):
        return self.operator.call(
            "RemoveMetadataConfiguration", ProfileToken=ProfileToken
        )

    def RemoveAudioOutputConfiguration(self, ProfileToken):
        return self.operator.call(
            "RemoveAudioOutputConfiguration", ProfileToken=ProfileToken
        )

    def RemoveAudioDecoderConfiguration(self, ProfileToken):
        return self.operator.call(
            "RemoveAudioDecoderConfiguration", ProfileToken=ProfileToken
        )

    def DeleteProfile(self, ProfileToken):
        return self.operator.call("DeleteProfile", ProfileToken=ProfileToken)

    def GetVideoSourceConfigurations(self):
        return self.operator.call("GetVideoSourceConfigurations")

    def GetVideoEncoderConfigurations(self):
        return self.operator.call("GetVideoEncoderConfigurations")

    def GetAudioSourceConfigurations(self):
        return self.operator.call("GetAudioSourceConfigurations")

    def GetAudioEncoderConfigurations(self):
        return self.operator.call("GetAudioEncoderConfigurations")

    def GetVideoAnalyticsConfigurations(self):
        return self.operator.call("GetVideoAnalyticsConfigurations")

    def GetMetadataConfigurations(self):
        return self.operator.call("GetMetadataConfigurations")

    def GetAudioOutputConfigurations(self):
        return self.operator.call("GetAudioOutputConfigurations")

    def GetAudioDecoderConfigurations(self):
        return self.operator.call("GetAudioDecoderConfigurations")

    def GetVideoSourceConfiguration(self, ConfigurationToken):
        return self.operator.call(
            "GetVideoSourceConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetVideoEncoderConfiguration(self, ConfigurationToken):
        return self.operator.call(
            "GetVideoEncoderConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetAudioSourceConfiguration(self, ConfigurationToken):
        return self.operator.call(
            "GetAudioSourceConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetAudioEncoderConfiguration(self, ConfigurationToken):
        return self.operator.call(
            "GetAudioEncoderConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetVideoAnalyticsConfiguration(self, ConfigurationToken):
        return self.operator.call(
            "GetVideoAnalyticsConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetMetadataConfiguration(self, ConfigurationToken):
        return self.operator.call(
            "GetMetadataConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetAudioOutputConfiguration(self, ConfigurationToken):
        return self.operator.call(
            "GetAudioOutputConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetAudioDecoderConfiguration(self, ConfigurationToken):
        return self.operator.call(
            "GetAudioDecoderConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetCompatibleVideoEncoderConfigurations(self, ProfileToken):
        return self.operator.call(
            "GetCompatibleVideoEncoderConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleVideoSourceConfigurations(self, ProfileToken):
        return self.operator.call(
            "GetCompatibleVideoSourceConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleAudioEncoderConfigurations(self, ProfileToken):
        return self.operator.call(
            "GetCompatibleAudioEncoderConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleAudioSourceConfigurations(self, ProfileToken):
        return self.operator.call(
            "GetCompatibleAudioSourceConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleVideoAnalyticsConfigurations(self, ProfileToken):
        return self.operator.call(
            "GetCompatibleVideoAnalyticsConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleMetadataConfigurations(self, ProfileToken):
        return self.operator.call(
            "GetCompatibleMetadataConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleAudioOutputConfigurations(self, ProfileToken):
        return self.operator.call(
            "GetCompatibleAudioOutputConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleAudioDecoderConfigurations(self, ProfileToken):
        return self.operator.call(
            "GetCompatibleAudioDecoderConfigurations", ProfileToken=ProfileToken
        )

    def SetVideoSourceConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetVideoSourceConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetVideoEncoderConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetVideoEncoderConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioSourceConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetAudioSourceConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioEncoderConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetAudioEncoderConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetVideoAnalyticsConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetVideoAnalyticsConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetMetadataConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetMetadataConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioOutputConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetAudioOutputConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioDecoderConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetAudioDecoderConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

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

    def GetGuaranteedNumberOfVideoEncoderInstances(self, ConfigurationToken):
        return self.operator.call(
            "GetGuaranteedNumberOfVideoEncoderInstances",
            ConfigurationToken=ConfigurationToken,
        )

    def GetStreamUri(self, StreamSetup, ProfileToken):
        return self.operator.call(
            "GetStreamUri", StreamSetup=StreamSetup, ProfileToken=ProfileToken
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

    def GetOSDs(self, ConfigurationToken=None):
        return self.operator.call("GetOSDs", ConfigurationToken=ConfigurationToken)

    def GetOSD(self, OSDToken):
        return self.operator.call("GetOSD", OSDToken=OSDToken)

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
