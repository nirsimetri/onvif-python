"""Media2 service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-many-public-methods
class Media2(ONVIFService):
    """Media2 service client.

    References:
        - First introduced: ONVIF Release 2.61 (December 2015)
        - Binding name: `Media2Binding` (ver20/media/wsdl/media.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/media/wsdl/media.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Media2.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("media2", "ver20")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Media2",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the media service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def CreateProfile(self, Name, Configuration=None):
        """This operation creates a new media profile.

        A created profile created via this method may be deleted via the DeleteProfile
        method. Optionally Configurations can be assinged to the profile on creation.
        For details regarding profile assignement check also the method
        AddConfiguration.
        """
        return self.operator.call(
            "CreateProfile", Name=Name, Configuration=Configuration
        )

    def GetProfiles(self, Token=None, Type=None):
        """Retrieve the profile with the specified token or all defined media profiles.

        - If no Type is provided the returned profiles shall contain no configuration
        information.

        - If a single Type with value 'All' is provided the returned profiles shall
        include all associated configurations.

        - Otherwise the requested list of configurations shall for each profile include
        the configurations present as Type.
        """
        return self.operator.call("GetProfiles", Token=Token, Type=Type)

    def AddConfiguration(self, ProfileToken, Name=None, Configuration=None):
        """This operation adds one or more Configurations to an existing media profile.

        If a configuration exists in the media profile, it will be replaced. A device
        shall support adding a compatible Configuration to a Profile containing a
        VideoSourceConfiguration and shall support streaming video data of such a
        profile.

        Note that OSD elements must be added via the CreateOSD command.
        """
        return self.operator.call(
            "AddConfiguration",
            ProfileToken=ProfileToken,
            Name=Name,
            Configuration=Configuration,
        )

    def RemoveConfiguration(self, ProfileToken, Configuration):
        """This operation removes the listed configurations from an existing media
        profile.

        If the media profile does not contain one of the listed configurations that item
        shall be ignored.
        """
        return self.operator.call(
            "RemoveConfiguration",
            ProfileToken=ProfileToken,
            Configuration=Configuration,
        )

    def DeleteProfile(self, Token):
        """This operation deletes a profile.

        Deletion of a profile is only possible for non-fixed profiles
        """
        return self.operator.call("DeleteProfile", Token=Token)

    def GetVideoSourceConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        """By default this operation lists all existing video source configurations for
        a device.

        Provide a profile token to list only configurations that are compatible with the
        profile. If a configuration token is provided only a single configuration will
        be returned.
        """
        return self.operator.call(
            "GetVideoSourceConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetVideoEncoderConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        """By default this operation lists all existing video encoder configurations for
        a device.

        Provide a profile token to list only configurations that are compatible with the
        profile. If a configuration token is provided only a single configuration will
        be returned.
        """
        return self.operator.call(
            "GetVideoEncoderConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioSourceConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        """By default this operation lists all existing audio source configurations for
        a device.

        Provide a profile token to list only configurations that are compatible with the
        profile. If a configuration token is provided only a single configuration will
        be returned.
        """
        return self.operator.call(
            "GetAudioSourceConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioEncoderConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        """By default this operation lists all existing audio encoder configurations for
        a device.

        Provide a profile token to list only configurations that are compatible with the
        profile. If a configuration token is provided only a single configuration will
        be returned.
        """
        return self.operator.call(
            "GetAudioEncoderConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAnalyticsConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        """By default this operation lists all existing video analytics configurations
        for a device.

        Provide a profile token to list only configurations that are compatible with the
        profile. If a configuration token is provided only a single configuration will
        be returned.
        """
        return self.operator.call(
            "GetAnalyticsConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetMetadataConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        """By default this operation lists all existing metadata configurations for a
        device.

        Provide a profile token to list only configurations that are compatible with the
        profile. If a configuration token is provided only a single configuration will
        be returned.
        """
        return self.operator.call(
            "GetMetadataConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioOutputConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        """By default this operation lists all existing audio output configurations for
        a device.

        Provide a profile token to list only configurations that are compatible with the
        profile. If a configuration token is provided only a single configuration will
        be returned.
        """
        return self.operator.call(
            "GetAudioOutputConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def GetAudioDecoderConfigurations(self, ConfigurationToken=None, ProfileToken=None):
        """By default this operation lists all existing audio decoder configurations for
        a device.

        Provide a profile token to list only configurations that are compatible with the
        profile. If a configuration token is provided only a single configuration will
        be returned.
        """
        return self.operator.call(
            "GetAudioDecoderConfigurations",
            ConfigurationToken=ConfigurationToken,
            ProfileToken=ProfileToken,
        )

    def SetVideoSourceConfiguration(self, Configuration):
        """This operation modifies a video source configuration.

        Running streams using this configuration may be immediately updated according to
        the new settings. The changes are not guaranteed to take effect unless the
        client requests a new stream URI and restarts any affected stream. NVC methods
        for changing a running stream are out of scope for this specification.
        """
        return self.operator.call(
            "SetVideoSourceConfiguration", Configuration=Configuration
        )

    def SetVideoEncoderConfiguration(self, Configuration):
        """This operation modifies a video encoder configuration.

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
            "SetVideoEncoderConfiguration", Configuration=Configuration
        )

    def SetAudioSourceConfiguration(self, Configuration):
        """This operation modifies an audio source configuration.

        Running streams using this configuration may be immediately updated according to
        the new settings. The changes are not guaranteed to take effect unless the
        client requests a new stream URI and restarts any affected stream NVC methods
        for changing a running stream are out of scope for this specification.
        """
        return self.operator.call(
            "SetAudioSourceConfiguration", Configuration=Configuration
        )

    def SetAudioEncoderConfiguration(self, Configuration):
        """This operation modifies an audio encoder configuration.

        Running streams using this configuration may be immediately updated according to
        the new settings. The changes are not guaranteed to take effect unless the
        client requests a new stream URI and restarts any affected streams. NVC methods
        for changing a running stream are out of scope for this specification.
        """
        return self.operator.call(
            "SetAudioEncoderConfiguration", Configuration=Configuration
        )

    def SetMetadataConfiguration(self, Configuration):
        """This operation modifies a metadata configuration.

        Running streams using this configuration may be updated immediately according to
        the new settings. The changes are not guaranteed to take effect unless the
        client requests a new stream URI and restarts any affected streams. NVC methods
        for changing a running stream are out of scope for this specification.
        """
        return self.operator.call(
            "SetMetadataConfiguration", Configuration=Configuration
        )

    def SetAudioOutputConfiguration(self, Configuration):
        """This operation modifies an audio output configuration."""
        return self.operator.call(
            "SetAudioOutputConfiguration", Configuration=Configuration
        )

    def SetAudioDecoderConfiguration(self, Configuration):
        """This operation modifies an audio decoder configuration."""
        return self.operator.call(
            "SetAudioDecoderConfiguration", Configuration=Configuration
        )

    def SetEQPreset(self, Configuration):
        """This command is to configure Audio EQPreset."""
        return self.operator.call("SetEQPreset", Configuration=Configuration)

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
        audio output configuration parameters) for configuring an audio output.

        To retrieve the EQPresetList, a valid ConfigurationToken must be provided. If
        EQPreset is supported and isFrequencyDecibelEditable is signaled as true, the
        response shall include the FrequencyDecibelPair.
        """
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

    def GetVideoEncoderInstances(self, ConfigurationToken):
        """The GetVideoEncoderInstances command can be used to request the minimum
        number of guaranteed video encoder instances (applications) per Video Source
        Configuration."""
        return self.operator.call(
            "GetVideoEncoderInstances", ConfigurationToken=ConfigurationToken
        )

    def GetStreamUri(self, Protocol, ProfileToken):
        """This operation requests a URI that can be used to initiate a live media
        stream using RTSP as the control protocol.

        The returned URI shall remain valid indefinitely even if the profile is changed.

        Defined stream types are
        - RtspUnicast RTSP streaming RTP as UDP Unicast.
        - RtspMulticast RTSP streaming RTP as UDP Multicast.
        - RtspsUnicast Secure RTSP streaming with SRTP as UDP Unicast.
        - RtspsMulticast Secure RTSP streaming with SRTP as UDP Multicast.
        - RTSP RTSP streaming RTP over TCP.
        - RtspOverHttp Tunneling both the RTSP control channel and the RTP stream over
        HTTP or HTTPS.

        If a multicast stream is requested at least one of VideoEncoder2Configuration,
        AudioEncoder2Configuration and MetadataConfiguration shall have a valid
        multicast setting.

        For full compatibility with other ONVIF services a device should not generate
        Uris longer than 128 octets.
        """
        return self.operator.call(
            "GetStreamUri", Protocol=Protocol, ProfileToken=ProfileToken
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
        """This command stops multicast streaming using a specified media profile of a
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
        The URI can be used for acquiring a JPEG image through an HTTP GET operation.
        The image encoding will always be JPEG regardless of the encoding setting in the
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

    def GetOSDs(self, OSDToken=None, ConfigurationToken=None):
        """This operation lists existing OSD configurations for the device.

        - If an OSD token is provided the device shall respond with the requested
        configuration or provide an error if it does not exist.

        - In case only a video source configuration token is provided the device shall
        respond with all configurations that exist for the video source configuration.

        - If no tokens are provided the device shall respond with all available OSD
        configurations.
        """
        return self.operator.call(
            "GetOSDs", OSDToken=OSDToken, ConfigurationToken=ConfigurationToken
        )

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

    def GetMasks(self, Token=None, ConfigurationToken=None):
        """This operation lists existing Mask configurations for the device.

        - If an Mask token is provided the device shall respond with the requested
        configuration or provide an error if it does not exist.

        - In case only a video source configuration token is provided the device shall
        respond with all configurations that exist for the video source configuration.

        - If no tokens are provided the device shall respond with all available Mask
        configurations.
        """
        return self.operator.call(
            "GetMasks", Token=Token, ConfigurationToken=ConfigurationToken
        )

    def GetMaskOptions(self, ConfigurationToken):
        """Get the Mask Options."""
        return self.operator.call(
            "GetMaskOptions", ConfigurationToken=ConfigurationToken
        )

    def SetMask(self, Mask):
        """Set the Mask."""
        return self.operator.call("SetMask", Mask=Mask)

    def CreateMask(self, Mask):
        """Create the Mask."""
        return self.operator.call("CreateMask", Mask=Mask)

    def DeleteMask(self, Token):
        """Delete the Mask."""
        return self.operator.call("DeleteMask", Token=Token)

    def GetWebRTCConfigurations(self):
        """This operation gets the current WebRTC configuration for the device."""
        return self.operator.call("GetWebRTCConfigurations")

    def SetWebRTCConfigurations(self, WebRTCConfiguration=None):
        """This operation sets the WebRTC configuration for the device."""
        return self.operator.call(
            "SetWebRTCConfigurations", WebRTCConfiguration=WebRTCConfiguration
        )

    def GetAudioClips(self, Token=None):
        """This operation retrieves audio clip configurations from the device.

        If an audio clip token is provided, the device shall return the audio clip
        configuration associated with that token. If no token is provided, the device
        shall return all audio clip configurations that exist on the device.
        """
        return self.operator.call("GetAudioClips", Token=Token)

    def AddAudioClip(self, Configuration, Token=None):
        """This operation adds audio clip configuration to the device and provides audio
        clip upload URI to the client.

        The response to the command includes an HTTP URL to which the audio clip may be
        uploaded within the expiry time. If the client is unable to upload the audio
        clip within the URL's expiry time, the associated audio clip configuration will
        be permanently removed from the device.
        """
        return self.operator.call(
            "AddAudioClip", Token=Token, Configuration=Configuration
        )

    def SetAudioClip(self, Token, Configuration):
        """This operation modifies the existing audio clip configuration on the
        device."""
        return self.operator.call(
            "SetAudioClip", Token=Token, Configuration=Configuration
        )

    def DeleteAudioClip(self, Token):
        """This operation deletes the audio clip configuration and the associated audio
        clip on the device.

        The audio clip should be de-associated from the event or schedule trigger if it
        was previously associated before this operation. This operation will fail if the
        device is playing the audio clip at the same time due to user operation,
        schedule, or event trigger.
        """
        return self.operator.call("DeleteAudioClip", Token=Token)

    def PlayAudioClip(self, Token, Play, AudioOutputToken=None, RepeatCycles=None):
        """This operation plays or stops the ongoing audio clip on the device."""
        return self.operator.call(
            "PlayAudioClip",
            Token=Token,
            AudioOutputToken=AudioOutputToken,
            Play=Play,
            RepeatCycles=RepeatCycles,
        )

    def AddTTSAudioClip(self, Configuration, TTSConfiguration, Token=None):
        """This operation sends a text and its configuartion to device that supports TTS
        function, so that device could convert the text into an audio clip and play it
        according to audio clip Configuration and TTS Configuration."""
        return self.operator.call(
            "AddTTSAudioClip",
            Token=Token,
            Configuration=Configuration,
            TTSConfiguration=TTSConfiguration,
        )

    def GetPlayingAudioClips(self):
        """This operation retrieves audio clips information which are playing currently
        in the device."""
        return self.operator.call("GetPlayingAudioClips")

    def GetMulticastAudioDecoderConfigurationOptions(self, ConfigurationToken=None):
        """This operation gets the available options for the MulticastAudioDecoder
        configuration."""
        return self.operator.call(
            "GetMulticastAudioDecoderConfigurationOptions",
            ConfigurationToken=ConfigurationToken,
        )

    def GetMulticastAudioDecoderConfigurations(self, ConfigurationToken=None):
        """This operation gets the list of multicast audio decoder configurations."""
        return self.operator.call(
            "GetMulticastAudioDecoderConfigurations",
            ConfigurationToken=ConfigurationToken,
        )

    def SetMulticastAudioDecoderConfiguration(self, Configuration):
        """This operation sets the MulticastAudioDecoderConfiguration."""
        return self.operator.call(
            "SetMulticastAudioDecoderConfiguration", Configuration=Configuration
        )
