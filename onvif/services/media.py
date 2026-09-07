"""Media service implementation."""

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-many-public-methods
class Media(ONVIFService):
    """Media service client.

    References:
        - First introduced: ONVIF Release 2.1 (June 2011) Split from Core 2.0
        - Binding name: `MediaBinding` (ver10/media/wsdl/media.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/media/wsdl/media.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Media.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("media")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Media",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the media service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetVideoSources(self):
        """This command lists all available physical video inputs of the device."""
        return self.operator.call("GetVideoSources")

    def GetAudioSources(self):
        """This command lists all available physical audio inputs of the device."""
        return self.operator.call("GetAudioSources")

    def GetAudioOutputs(self):
        """This command lists all available physical audio outputs of the device."""
        return self.operator.call("GetAudioOutputs")

    def CreateProfile(self, Name, Token=None):
        """This operation creates a new empty media profile.

        The media profile shall be created in the device and shall be persistent (remain
        after reboot). A created profile shall be deletable and a device shall set the
        "fixed" attribute to false in the returned Profile.
        """
        return self.operator.call("CreateProfile", Name=Name, Token=Token)

    def GetProfile(self, ProfileToken):
        """If the profile token is already known, a profile can be fetched through the
        GetProfile command."""
        return self.operator.call("GetProfile", ProfileToken=ProfileToken)

    def GetProfiles(self):
        """Any endpoint can ask for the existing media profiles of a device using the
        GetProfiles command.

        Pre-configured or dynamically configured profiles can be retrieved using this
        command. This command lists all configured profiles in a device. The client does
        not need to know the media profile in order to use the command.
        """
        return self.operator.call("GetProfiles")

    def AddVideoEncoderConfiguration(self, ProfileToken, ConfigurationToken):
        """This operation adds a VideoEncoderConfiguration to an existing media profile.

        If a configuration exists in the media profile, it will be replaced. The change
        shall be persistent. A device shall support adding a compatible
        VideoEncoderConfiguration to a Profile containing a VideoSourceConfiguration and
        shall support streaming video data of such a profile.
        """
        return self.operator.call(
            "AddVideoEncoderConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddVideoSourceConfiguration(self, ProfileToken, ConfigurationToken):
        """This operation adds a VideoSourceConfiguration to an existing media profile.

        If such a configuration exists in the media profile, it will be replaced. The
        change shall be persistent.
        """
        return self.operator.call(
            "AddVideoSourceConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddAudioEncoderConfiguration(self, ProfileToken, ConfigurationToken):
        """This operation adds an AudioEncoderConfiguration to an existing media
        profile.

        If a configuration exists in the media profile, it will be replaced. The change
        shall be persistent. A device shall support adding a compatible
        AudioEncoderConfiguration to a profile containing an AudioSourceConfiguration
        and shall support streaming audio data of such a profile.
        """
        return self.operator.call(
            "AddAudioEncoderConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddAudioSourceConfiguration(self, ProfileToken, ConfigurationToken):
        """This operation adds an AudioSourceConfiguration to an existing media profile.

        If a configuration exists in the media profile, it will be replaced. The change
        shall be persistent.
        """
        return self.operator.call(
            "AddAudioSourceConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddPTZConfiguration(self, ProfileToken, ConfigurationToken):
        """This operation adds a PTZConfiguration to an existing media profile.

        If a configuration exists in the media profile, it will be replaced. The change
        shall be persistent. Adding a PTZConfiguration to a media profile means that
        streams using that media profile can contain PTZ status (in the metadata), and
        that the media profile can be used for controlling PTZ movement.
        """
        return self.operator.call(
            "AddPTZConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddVideoAnalyticsConfiguration(self, ProfileToken, ConfigurationToken):
        """This operation adds a VideoAnalytics configuration to an existing media
        profile.

        If a configuration exists in the media profile, it will be replaced. The change
        shall be persistent. Adding a VideoAnalyticsConfiguration to a media profile
        means that streams using that media profile can contain video analytics data (in
        the metadata) as defined by the submitted configuration reference. A profile
        containing only a video analytics configuration but no video source
        configuration is incomplete. Therefore, a client should first add a video source
        configuration to a profile before adding a video analytics configuration. The
        device can deny adding of a video analytics configuration before a video source
        configuration.
        """
        return self.operator.call(
            "AddVideoAnalyticsConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddMetadataConfiguration(self, ProfileToken, ConfigurationToken):
        """This operation adds a Metadata configuration to an existing media profile.

        If a configuration exists in the media profile, it will be replaced. The change
        shall be persistent. Adding a MetadataConfiguration to a Profile means that
        streams using that profile contain metadata. Metadata can consist of events, PTZ
        status, and/or video analytics data.
        """
        return self.operator.call(
            "AddMetadataConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddAudioOutputConfiguration(self, ProfileToken, ConfigurationToken):
        """This operation adds an AudioOutputConfiguration to an existing media profile.

        If a configuration exists in the media profile, it will be replaced. The change
        shall be persistent.
        """
        return self.operator.call(
            "AddAudioOutputConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def AddAudioDecoderConfiguration(self, ProfileToken, ConfigurationToken):
        """This operation adds an AudioDecoderConfiguration to an existing media
        profile.

        If a configuration exists in the media profile, it shall be replaced. The change
        shall be persistent.
        """
        return self.operator.call(
            "AddAudioDecoderConfiguration",
            ProfileToken=ProfileToken,
            ConfigurationToken=ConfigurationToken,
        )

    def RemoveVideoEncoderConfiguration(self, ProfileToken):
        """This operation removes a VideoEncoderConfiguration from an existing media
        profile.

        If the media profile does not contain a VideoEncoderConfiguration, the operation
        has no effect. The removal shall be persistent.
        """
        return self.operator.call(
            "RemoveVideoEncoderConfiguration", ProfileToken=ProfileToken
        )

    def RemoveVideoSourceConfiguration(self, ProfileToken):
        """This operation removes a VideoSourceConfiguration from an existing media
        profile.

        If the media profile does not contain a VideoSourceConfiguration, the operation
        has no effect. The removal shall be persistent. Video source configurations
        should only be removed after removing a VideoEncoderConfiguration from the media
        profile.
        """
        return self.operator.call(
            "RemoveVideoSourceConfiguration", ProfileToken=ProfileToken
        )

    def RemoveAudioEncoderConfiguration(self, ProfileToken):
        """This operation removes an AudioEncoderConfiguration from an existing media
        profile.

        If the media profile does not contain an AudioEncoderConfiguration, the
        operation has no effect. The removal shall be persistent.
        """
        return self.operator.call(
            "RemoveAudioEncoderConfiguration", ProfileToken=ProfileToken
        )

    def RemoveAudioSourceConfiguration(self, ProfileToken):
        """This operation removes an AudioSourceConfiguration from an existing media
        profile.

        If the media profile does not contain an AudioSourceConfiguration, the operation
        has no effect. The removal shall be persistent. Audio source configurations
        should only be removed after removing an AudioEncoderConfiguration from the
        media profile.
        """
        return self.operator.call(
            "RemoveAudioSourceConfiguration", ProfileToken=ProfileToken
        )

    def RemovePTZConfiguration(self, ProfileToken):
        """This operation removes a PTZConfiguration from an existing media profile.

        If the media profile does not contain a PTZConfiguration, the operation has no
        effect. The removal shall be persistent.
        """
        return self.operator.call("RemovePTZConfiguration", ProfileToken=ProfileToken)

    def RemoveVideoAnalyticsConfiguration(self, ProfileToken):
        """This operation removes a VideoAnalyticsConfiguration from an existing media
        profile.

        If the media profile does not contain a VideoAnalyticsConfiguration, the
        operation has no effect. The removal shall be persistent.
        """
        return self.operator.call(
            "RemoveVideoAnalyticsConfiguration", ProfileToken=ProfileToken
        )

    def RemoveMetadataConfiguration(self, ProfileToken):
        """This operation removes a MetadataConfiguration from an existing media
        profile.

        If the media profile does not contain a MetadataConfiguration, the operation has
        no effect. The removal shall be persistent.
        """
        return self.operator.call(
            "RemoveMetadataConfiguration", ProfileToken=ProfileToken
        )

    def RemoveAudioOutputConfiguration(self, ProfileToken):
        """This operation removes an AudioOutputConfiguration from an existing media
        profile.

        If the media profile does not contain an AudioOutputConfiguration, the operation
        has no effect. The removal shall be persistent.
        """
        return self.operator.call(
            "RemoveAudioOutputConfiguration", ProfileToken=ProfileToken
        )

    def RemoveAudioDecoderConfiguration(self, ProfileToken):
        """This operation removes an AudioDecoderConfiguration from an existing media
        profile.

        If the media profile does not contain an AudioDecoderConfiguration, the
        operation has no effect. The removal shall be persistent.
        """
        return self.operator.call(
            "RemoveAudioDecoderConfiguration", ProfileToken=ProfileToken
        )

    def DeleteProfile(self, ProfileToken):
        """This operation deletes a profile.

        This change shall always be persistent. Deletion of a profile is only possible
        for non-fixed profiles
        """
        return self.operator.call("DeleteProfile", ProfileToken=ProfileToken)

    def GetVideoSourceConfigurations(self):
        """This operation lists all existing video source configurations for a device.

        The client need not know anything about the video source configurations in order
        to use the command.
        """
        return self.operator.call("GetVideoSourceConfigurations")

    def GetVideoEncoderConfigurations(self):
        """This operation lists all existing video encoder configurations of a device.

        This command lists all configured video encoder configurations in a device. The
        client need not know anything apriori about the video encoder configurations in
        order to use the command.
        """
        return self.operator.call("GetVideoEncoderConfigurations")

    def GetAudioSourceConfigurations(self):
        """This operation lists all existing audio source configurations of a device.

        This command lists all audio source configurations in a device. The client need
        not know anything apriori about the audio source configurations in order to use
        the command.
        """
        return self.operator.call("GetAudioSourceConfigurations")

    def GetAudioEncoderConfigurations(self):
        """This operation lists all existing device audio encoder configurations.

        The client need not know anything apriori about the audio encoder configurations
        in order to use the command.
        """
        return self.operator.call("GetAudioEncoderConfigurations")

    def GetVideoAnalyticsConfigurations(self):
        """This operation lists all video analytics configurations of a device.

        This command lists all configured video analytics in a device. The client need
        not know anything apriori about the video analytics in order to use the command.
        """
        return self.operator.call("GetVideoAnalyticsConfigurations")

    def GetMetadataConfigurations(self):
        """This operation lists all existing metadata configurations.

        The client need not know anything apriori about the metadata in order to use the
        command.
        """
        return self.operator.call("GetMetadataConfigurations")

    def GetAudioOutputConfigurations(self):
        """This command lists all existing AudioOutputConfigurations of a device.

        The NVC need not know anything apriori about the audio configurations to use
        this command.
        """
        return self.operator.call("GetAudioOutputConfigurations")

    def GetAudioDecoderConfigurations(self):
        """This command lists all existing AudioDecoderConfigurations of a device.

        The NVC need not know anything apriori about the audio decoder configurations in
        order to use this command.
        """
        return self.operator.call("GetAudioDecoderConfigurations")

    def GetVideoSourceConfiguration(self, ConfigurationToken):
        """If the video source configuration token is already known, the video source
        configuration can be fetched through the GetVideoSourceConfiguration command."""
        return self.operator.call(
            "GetVideoSourceConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetVideoEncoderConfiguration(self, ConfigurationToken):
        """If the video encoder configuration token is already known, the encoder
        configuration can be fetched through the GetVideoEncoderConfiguration
        command."""
        return self.operator.call(
            "GetVideoEncoderConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetAudioSourceConfiguration(self, ConfigurationToken):
        """The GetAudioSourceConfiguration command fetches the audio source
        configurations if the audio source configuration token is already known."""
        return self.operator.call(
            "GetAudioSourceConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetAudioEncoderConfiguration(self, ConfigurationToken):
        """The GetAudioEncoderConfiguration command fetches the encoder configuration if
        the audio encoder configuration token is known."""
        return self.operator.call(
            "GetAudioEncoderConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetVideoAnalyticsConfiguration(self, ConfigurationToken):
        """The GetVideoAnalyticsConfiguration command fetches the video analytics
        configuration if the video analytics token is known."""
        return self.operator.call(
            "GetVideoAnalyticsConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetMetadataConfiguration(self, ConfigurationToken):
        """The GetMetadataConfiguration command fetches the metadata configuration if
        the metadata token is known."""
        return self.operator.call(
            "GetMetadataConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetAudioOutputConfiguration(self, ConfigurationToken):
        """If the audio output configuration token is already known, the output
        configuration can be fetched through the GetAudioOutputConfiguration command."""
        return self.operator.call(
            "GetAudioOutputConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetAudioDecoderConfiguration(self, ConfigurationToken):
        """If the audio decoder configuration token is already known, the decoder
        configuration can be fetched through the GetAudioDecoderConfiguration
        command."""
        return self.operator.call(
            "GetAudioDecoderConfiguration", ConfigurationToken=ConfigurationToken
        )

    def GetCompatibleVideoEncoderConfigurations(self, ProfileToken):
        """This operation lists all the video encoder configurations of the device that
        are compatible with a certain media profile.

        Each of the returned configurations shall be a valid input parameter for the
        AddVideoEncoderConfiguration command on the media profile. The result will vary
        depending on the capabilities, configurations and settings in the device.
        """
        return self.operator.call(
            "GetCompatibleVideoEncoderConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleVideoSourceConfigurations(self, ProfileToken):
        """This operation requests all the video source configurations of the device
        that are compatible with a certain media profile.

        Each of the returned configurations shall be a valid input parameter for the
        AddVideoSourceConfiguration command on the media profile. The result will vary
        depending on the capabilities, configurations and settings in the device.
        """
        return self.operator.call(
            "GetCompatibleVideoSourceConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleAudioEncoderConfigurations(self, ProfileToken):
        """This operation requests all audio encoder configurations of a device that are
        compatible with a certain media profile.

        Each of the returned configurations shall be a valid input parameter for the
        AddAudioSourceConfiguration command on the media profile. The result varies
        depending on the capabilities, configurations and settings in the device.
        """
        return self.operator.call(
            "GetCompatibleAudioEncoderConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleAudioSourceConfigurations(self, ProfileToken):
        """This operation requests all audio source configurations of the device that
        are compatible with a certain media profile.

        Each of the returned configurations shall be a valid input parameter for the
        AddAudioEncoderConfiguration command on the media profile. The result varies
        depending on the capabilities, configurations and settings in the device.
        """
        return self.operator.call(
            "GetCompatibleAudioSourceConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleVideoAnalyticsConfigurations(self, ProfileToken):
        """This operation requests all video analytic configurations of the device that
        are compatible with a certain media profile.

        Each of the returned configurations shall be a valid input parameter for the
        AddVideoAnalyticsConfiguration command on the media profile. The result varies
        depending on the capabilities, configurations and settings in the device.
        """
        return self.operator.call(
            "GetCompatibleVideoAnalyticsConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleMetadataConfigurations(self, ProfileToken):
        """This operation requests all the metadata configurations of the device that
        are compatible with a certain media profile.

        Each of the returned configurations shall be a valid input parameter for the
        AddMetadataConfiguration command on the media profile. The result varies
        depending on the capabilities, configurations and settings in the device.
        """
        return self.operator.call(
            "GetCompatibleMetadataConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleAudioOutputConfigurations(self, ProfileToken):
        """This command lists all audio output configurations of a device that are
        compatible with a certain media profile.

        Each returned configuration shall be a valid input for the
        AddAudioOutputConfiguration command.
        """
        return self.operator.call(
            "GetCompatibleAudioOutputConfigurations", ProfileToken=ProfileToken
        )

    def GetCompatibleAudioDecoderConfigurations(self, ProfileToken):
        """This operation lists all the audio decoder configurations of the device that
        are compatible with a certain media profile.

        Each of the returned configurations shall be a valid input parameter for the
        AddAudioDecoderConfiguration command on the media profile.
        """
        return self.operator.call(
            "GetCompatibleAudioDecoderConfigurations", ProfileToken=ProfileToken
        )

    def SetVideoSourceConfiguration(self, Configuration, ForcePersistence):
        """This operation modifies a video source configuration.

        The ForcePersistence flag indicates if the changes shall remain after reboot of
        the device. Running streams using this configuration may be immediately updated
        according to the new settings. The changes are not guaranteed to take effect
        unless the client requests a new stream URI and restarts any affected stream.
        NVC methods for changing a running stream are out of scope for this
        specification.
        """
        return self.operator.call(
            "SetVideoSourceConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetVideoEncoderConfiguration(self, Configuration, ForcePersistence):
        """This operation modifies a video encoder configuration.

        The ForcePersistence flag indicates if the changes shall remain after reboot of
        the device. Changes in the Multicast settings shall always be persistent.
        Running streams using this configuration may be immediately updated according to
        the new settings. The changes are not guaranteed to take effect unless the
        client requests a new stream URI and restarts any affected stream. NVC methods
        for changing a running stream are out of scope for this specification.

        SessionTimeout is provided as a hint for keeping rtsp session by a device. If
        necessary the device may adapt parameter values for SessionTimeout elements
        without returning an error. For the time between keep alive calls the client
        shall adhere to the timeout value signaled via RTSP.
        """
        return self.operator.call(
            "SetVideoEncoderConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioSourceConfiguration(self, Configuration, ForcePersistence):
        """This operation modifies an audio source configuration.

        The ForcePersistence flag indicates if the changes shall remain after reboot of
        the device. Running streams using this configuration may be immediately updated
        according to the new settings. The changes are not guaranteed to take effect
        unless the client requests a new stream URI and restarts any affected stream NVC
        methods for changing a running stream are out of scope for this specification.
        """
        return self.operator.call(
            "SetAudioSourceConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioEncoderConfiguration(self, Configuration, ForcePersistence):
        """This operation modifies an audio encoder configuration.

        The ForcePersistence flag indicates if the changes shall remain after reboot of
        the device. Running streams using this configuration may be immediately updated
        according to the new settings. The changes are not guaranteed to take effect
        unless the client requests a new stream URI and restarts any affected streams.
        NVC methods for changing a running stream are out of scope for this
        specification.
        """
        return self.operator.call(
            "SetAudioEncoderConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetVideoAnalyticsConfiguration(self, Configuration, ForcePersistence):
        """A video analytics configuration is modified using this command.

        The ForcePersistence flag indicates if the changes shall remain after reboot of
        the device or not. Running streams using this configuration shall be immediately
        updated according to the new settings. Otherwise inconsistencies can occur
        between the scene description processed by the rule engine and the notifications
        produced by analytics engine and rule engine which reference the very same video
        analytics configuration token.
        """
        return self.operator.call(
            "SetVideoAnalyticsConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetMetadataConfiguration(self, Configuration, ForcePersistence):
        """This operation modifies a metadata configuration.

        The ForcePersistence flag indicates if the changes shall remain after reboot of
        the device. Changes in the Multicast settings shall always be persistent.
        Running streams using this configuration may be updated immediately according to
        the new settings. The changes are not guaranteed to take effect unless the
        client requests a new stream URI and restarts any affected streams. NVC methods
        for changing a running stream are out of scope for this specification.
        """
        return self.operator.call(
            "SetMetadataConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioOutputConfiguration(self, Configuration, ForcePersistence):
        """This operation modifies an audio output configuration.

        The ForcePersistence flag indicates if the changes shall remain after reboot of
        the device.
        """
        return self.operator.call(
            "SetAudioOutputConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioDecoderConfiguration(self, Configuration, ForcePersistence):
        """This operation modifies an audio decoder configuration.

        The ForcePersistence flag indicates if the changes shall remain after reboot of
        the device.
        """
        return self.operator.call(
            "SetAudioDecoderConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def GetVideoSourceConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        """This operation returns the available options (supported values and ranges for
        video source configuration parameters) when the video source parameters are
        reconfigured If a video source configuration is specified, the options shall
        concern that particular configuration.

        If a media profile is specified, the options shall be compatible with that media
        profile.
        """
        return self.operator.call(
            "GetVideoSourceConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetVideoEncoderConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        """This operation returns the available options (supported values and ranges for
        video encoder configuration parameters) when the video encoder parameters are
        reconfigured.

        For JPEG, MPEG4 and H264 extension elements have been defined that provide
        additional information. A device must provide the XxxOption information for all
        encodings supported and should additionally provide the corresponding XxxOption2
        information.

        This response contains the available video encoder configuration options. If a
        video encoder configuration is specified, the options shall concern that
        particular configuration. If a media profile is specified, the options shall be
        compatible with that media profile. If no tokens are specified, the options
        shall be considered generic for the device.
        """
        return self.operator.call(
            "GetVideoEncoderConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioSourceConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        """This operation returns the available options (supported values and ranges for
        audio source configuration parameters) when the audio source parameters are
        reconfigured.

        If an audio source configuration is specified, the options shall concern that
        particular configuration. If a media profile is specified, the options shall be
        compatible with that media profile.
        """
        return self.operator.call(
            "GetAudioSourceConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioEncoderConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        """This operation returns the available options (supported values and ranges for
        audio encoder configuration parameters) when the audio encoder parameters are
        reconfigured."""
        return self.operator.call(
            "GetAudioEncoderConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetMetadataConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        """This operation returns the available options (supported values and ranges for
        metadata configuration parameters) for changing the metadata configuration."""
        return self.operator.call(
            "GetMetadataConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioOutputConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        """This operation returns the available options (supported values and ranges for
        audio output configuration parameters) for configuring an audio output."""
        return self.operator.call(
            "GetAudioOutputConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioDecoderConfigurationOptions(
        self, ConfigurationToken=None, ProfileToken=None
    ):
        """This command list the audio decoding capabilities for a given profile and
        configuration of a device."""
        return self.operator.call(
            "GetAudioDecoderConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetGuaranteedNumberOfVideoEncoderInstances(self, ConfigurationToken):
        """The GetGuaranteedNumberOfVideoEncoderInstances command can be used to request
        the minimum number of guaranteed video encoder instances (applications) per
        Video Source Configuration."""
        return self.operator.call(
            "GetGuaranteedNumberOfVideoEncoderInstances",
            ConfigurationToken=ConfigurationToken,
        )

    def GetStreamUri(self, StreamSetup, ProfileToken):
        """This operation requests a URI that can be used to initiate a live media
        stream using RTSP as the control protocol.

        The returned URI shall remain valid indefinitely even if the profile is changed.
        The ValidUntilConnect, ValidUntilReboot and Timeout Parameter shall be set
        accordingly (ValidUntilConnect=false, ValidUntilReboot=false, timeout=PT0S).

        The correct syntax for the StreamSetup element for these media stream setups
        defined in 5.1.1 of the streaming specification are as follows:

        1. RTP unicast over UDP: StreamType = "RTP_unicast", TransportProtocol = "UDP"
        2. RTP over RTSP over HTTP over TCP: StreamType = "RTP_unicast", TransportProtocol = "HTTP"
        3. RTP over RTSP over TCP: StreamType = "RTP_unicast", TransportProtocol = "RTSP"

        If a multicast stream is requested at least one of VideoEncoderConfiguration,
        AudioEncoderConfiguration and MetadataConfiguration shall have a valid multicast
        setting.

        For full compatibility with other ONVIF services a device should not generate
        Uris longer than 128 octets.
        """
        return self.operator.call(
            "GetStreamUri", StreamSetup=StreamSetup, ProfileToken=ProfileToken
        )

    def StartMulticastStreaming(self, ProfileToken):
        """This command starts multicast streaming using a specified media profile of a
        device.

        Streaming continues until StopMulticastStreaming is called for the same Profile.
        The streaming shall continue after a reboot of the device until a
        StopMulticastStreaming request is received. The multicast address, port and TTL
        are configured in the VideoEncoderConfiguration, AudioEncoderConfiguration and
        MetadataConfiguration respectively.
        """
        return self.operator.call("StartMulticastStreaming", ProfileToken=ProfileToken)

    def StopMulticastStreaming(self, ProfileToken):
        """This command stop multicast streaming using a specified media profile of a
        device."""
        return self.operator.call("StopMulticastStreaming", ProfileToken=ProfileToken)

    def SetSynchronizationPoint(self, ProfileToken):
        """Synchronization points allow clients to decode and correctly use all data
        after the synchronization point.

        For example, if a video stream is configured with a large I-frame distance and a
        client loses a single packet, the client does not display video until the next
        I-frame is transmitted. In such cases, the client can request a Synchronization
        Point which enforces the device to add an I-Frame as soon as possible. Clients
        can request Synchronization Points for profiles. The device shall add
        synchronization points for all streams associated with this profile. Similarly,
        a synchronization point is used to get an update on full PTZ or event status
        through the metadata stream. If a video stream is associated with the profile,
        an I-frame shall be added to this video stream. If a PTZ metadata stream is
        associated to the profile, the PTZ position shall be repeated within the
        metadata stream.
        """
        return self.operator.call("SetSynchronizationPoint", ProfileToken=ProfileToken)

    def GetSnapshotUri(self, ProfileToken):
        """A client uses the GetSnapshotUri command to obtain a JPEG snapshot from the
        device.

        The returned URI shall remain valid indefinitely even if the profile is changed.
        The ValidUntilConnect, ValidUntilReboot and Timeout Parameter shall be set
        accordingly (ValidUntilConnect=false, ValidUntilReboot=false, timeout=PT0S). The
        URI can be used for acquiring a JPEG image through an HTTP GET operation. The
        image encoding will always be JPEG regardless of the encoding setting in the
        media profile. The Jpeg settings (like resolution or quality) may be taken from
        the profile if suitable. The provided image will be updated automatically and
        independent from calls to GetSnapshotUri.
        """
        return self.operator.call("GetSnapshotUri", ProfileToken=ProfileToken)

    def GetVideoSourceModes(self, VideoSourceToken):
        """A device returns the information for current video source mode and settable
        video source modes of specified video source.

        A device that indicates a capability of VideoSourceModes shall support this
        command.
        """
        return self.operator.call(
            "GetVideoSourceModes", VideoSourceToken=VideoSourceToken
        )

    def SetVideoSourceMode(self, VideoSourceToken, VideoSourceModeToken):
        """SetVideoSourceMode changes the media profile structure relating to video
        source for the specified video source mode.

        A device that indicates a capability of VideoSourceModes shall support this
        command. The behavior after changing the mode is not defined in this
        specification.
        """
        return self.operator.call(
            "SetVideoSourceMode",
            VideoSourceToken=VideoSourceToken,
            VideoSourceModeToken=VideoSourceModeToken,
        )

    def GetOSDs(self, ConfigurationToken=None):
        """Get the OSDs."""
        return self.operator.call("GetOSDs", ConfigurationToken=ConfigurationToken)

    def GetOSD(self, OSDToken):
        """Get the OSD."""
        return self.operator.call("GetOSD", OSDToken=OSDToken)

    def GetOSDOptions(self, ConfigurationToken):
        """Get the OSD Options."""
        return self.operator.call(
            "GetOSDOptions", ConfigurationToken=ConfigurationToken
        )

    def SetOSD(self, OSD):
        """Set the OSD."""
        return self.operator.call("SetOSD", OSD=OSD)

    def CreateOSD(self, OSD):
        """Create the OSD."""
        return self.operator.call("CreateOSD", OSD=OSD)

    def DeleteOSD(self, OSDToken):
        """Delete the OSD."""
        return self.operator.call("DeleteOSD", OSDToken=OSDToken)
