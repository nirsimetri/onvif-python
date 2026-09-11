"""DeviceIO service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name,too-many-public-methods
class DeviceIO(ONVIFService):
    """DeviceIO service client.

    | Property | Details |
    | --- | --- |
    | **First introduced** | ONVIF Release 2.1 (June 2011) Split from Core 2.0 |
    | **Binding name** | `DeviceIOBinding` (`ver10/deviceio.wsdl`) |
    | **Operations** | [deviceio.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/deviceio.wsdl) |
    | **Specification** | [DeviceIo.xml](https://developer.onvif.org/pub/specs/branches/development/doc/DeviceIo.xml) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("deviceio")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="DeviceIO",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the device IO service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetRelayOutputOptions(self, RelayOutputToken=None):
        """Request the available settings and ranges for one or all relay outputs.

        A device that has one or more RelayOutputs should support this command.

        Two examples that illustrate usage:

        1) Device supports range PT1S to PT120S:

        ```
        <tmd:RelayOutputOptions token='44'>
          <tmd:Mode>Monostable</tmd:Mode>
          <tmd:DelayTimes>1 120</tmd:DelayTimes>
        </tmd:RelayOutputOptions>
        ```

        2) Device supports values PT0.5S, PT1S, PT2s and PT1M:

        ```
        <tmd:RelayOutputOptions token='123'>
          <tmd:Mode>Monostable</tmd:Mode>
          <tmd:DelayTimes>0.5 1 2 60</tmd:DelayTimes>
          <tmd:Discrete>True</tmd:Discrete>
        </tmd:RelayOutputOptions>
        ```
        """
        return self.operator.call(
            "GetRelayOutputOptions", RelayOutputToken=RelayOutputToken
        )

    def GetAudioSources(self):
        """List all available audio sources for the device.

        The device that has one or more audio sources shall support the listing of
        available audio inputs through the GetAudioSources command.
        """
        return self.operator.call("GetAudioSources")

    def GetAudioOutputs(self):
        """List all available audio outputs of a device.

        A device that has one ore more physical audio outputs shall support listing of
        available audio outputs through the GetAudioOutputs command.
        """
        return self.operator.call("GetAudioOutputs")

    def GetVideoSources(self):
        """List all available video sources for the device.

        The device that has one or more video inputs shall support the listing of
        available video sources through the GetVideoSources command.
        """
        return self.operator.call("GetVideoSources")

    def GetVideoOutputs(self):
        """List all available video outputs of a device.

        A device that has one or more physical video outputs shall support listing of
        available video outputs through the GetVideoOutputs command.
        """
        return self.operator.call("GetVideoOutputs")

    def GetVideoSourceConfiguration(self, VideoSourceToken):
        """Get the video source configurations of a VideoSource.

        A device with one or more video sources shall support the
        GetVideoSourceConfigurations command.

        This method is deprecated.
        """
        return self.operator.call(
            "GetVideoSourceConfiguration", VideoSourceToken=VideoSourceToken
        )

    def GetVideoOutputConfiguration(self, VideoOutputToken):
        """Get the configuration of a Video Output.

        A device that has one or more Video Outputs shall support the retrieval of the
        VideoOutputConfiguration through this command.
        """
        return self.operator.call(
            "GetVideoOutputConfiguration", VideoOutputToken=VideoOutputToken
        )

    def GetAudioSourceConfiguration(self, AudioSourceToken):
        """List the configuration of an Audio Input.

        A device with one or more audio inputs shall support the
        GetAudioSourceConfiguration command.

        This method is deprecated.
        """
        return self.operator.call(
            "GetAudioSourceConfiguration", AudioSourceToken=AudioSourceToken
        )

    def GetAudioOutputConfiguration(self, AudioOutputToken):
        """Request the current configuration of a physical Audio output.

        A device that has one or more AudioOutputs shall support the retrieval of the
        AudioOutputConfiguration through this command.

        This method is deprecated.
        """
        return self.operator.call(
            "GetAudioOutputConfiguration", AudioOutputToken=AudioOutputToken
        )

    def SetVideoSourceConfiguration(self, Configuration, ForcePersistence):
        """Modify a video input configuration.

        A device that has one or more video sources shall support the setting of the
        VideoSourceConfiguration through this command.

        This method is deprecated.
        """
        return self.operator.call(
            "SetVideoSourceConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetVideoOutputConfiguration(self, Configuration, ForcePersistence):
        """Modify a video output configuration.

        A device that has one or more video outputs shall support the setting of its
        video output configuration through this command.
        """
        return self.operator.call(
            "SetVideoOutputConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioSourceConfiguration(self, Configuration, ForcePersistence):
        """Modify an audio source configuration.

        A device that has a one or more audio sources shall support the setting of the
        AudioSourceConfiguration through this command.

        This method is deprecated.
        """
        return self.operator.call(
            "SetAudioSourceConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioOutputConfiguration(self, Configuration, ForcePersistence):
        """Modify an audio output configuration.

        A device that has one ore more audio outputs shall support the setting of the
        AudioOutputConfiguration through this command.

        This method is deprecated.
        """
        return self.operator.call(
            "SetAudioOutputConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def GetVideoSourceConfigurationOptions(self, VideoSourceToken):
        """Request the VideoSourceConfigurationOptions of a VideoSource.

        A device with one or more video sources shall support this command.

        This method is deprecated.
        """
        return self.operator.call(
            "GetVideoSourceConfigurationOptions", VideoSourceToken=VideoSourceToken
        )

    def GetVideoOutputConfigurationOptions(self, VideoOutputToken):
        """Request the VideoOutputConfigurationOptions of a VideoOutput.

        A device that has one or more video outputs shall support the retrieval of
        VideoOutputConfigurationOptions through this command.
        """
        return self.operator.call(
            "GetVideoOutputConfigurationOptions", VideoOutputToken=VideoOutputToken
        )

    def GetAudioSourceConfigurationOptions(self, AudioSourceToken):
        """Request the AudioSourceConfigurationOptions of an AudioSource.

        A device with one ore more AudioSources shall support this command.

        This method is deprecated.
        """
        return self.operator.call(
            "GetAudioSourceConfigurationOptions", AudioSourceToken=AudioSourceToken
        )

    def GetAudioOutputConfigurationOptions(self, AudioOutputToken):
        """Request the available settings and ranges for a physical Audio output.

        A device that has one or more AudioOutputs shall support this command.

        This method is deprecated.
        """
        return self.operator.call(
            "GetAudioOutputConfigurationOptions", AudioOutputToken=AudioOutputToken
        )

    def GetRelayOutputs(self):
        """This operation gets a list of all available relay outputs and their
        settings."""
        return self.operator.call("GetRelayOutputs")

    def SetRelayOutputSettings(self, RelayOutput, RelayOutputToken, Properties):
        """This operation sets the settings of a relay output.

        The relay can work in two relay modes:

        - Bistable - After setting the state, the relay remains in this state.
        - Monostable - After setting the state, the relay returns to its idle state after the specified time.
        The physical idle state of a relay output can be configured by setting the IdleState to 'open' or 'closed'
        (inversion of the relay behaviour).

        Idle State 'open' means that the relay is open when the relay state is set to 'inactive' through the trigger
        command (see Section 8.5.3) and closed when the state is set to 'active' through the same command.

        Idle State 'closed' means, that the relay is closed when the relay state is set to 'inactive' through the
        trigger command (see Section 8.5.3) and open when the state is set to 'active' through the same command.
        """
        return self.operator.call(
            "SetRelayOutputSettings",
            RelayOutput=RelayOutput,
            RelayOutputToken=RelayOutputToken,
            Properties=Properties,
        )

    def SetRelayOutputState(self, RelayOutputToken, LogicalState):
        """Modify the relay state."""
        return self.operator.call(
            "SetRelayOutputState",
            RelayOutputToken=RelayOutputToken,
            LogicalState=LogicalState,
        )

    def GetDigitalInputs(self):
        """This operation gets a list of all available digital inputs."""
        return self.operator.call("GetDigitalInputs")

    def GetDigitalInputConfigurationOptions(self, Token=None):
        """This operation lists what configuration is available for digital inputs."""
        return self.operator.call("GetDigitalInputConfigurationOptions", Token=Token)

    def SetDigitalInputConfigurations(self, DigitalInputs):
        """Modify a digital input configuration."""
        return self.operator.call(
            "SetDigitalInputConfigurations", DigitalInputs=DigitalInputs
        )

    def GetSerialPorts(self):
        """This operation gets a list of all available serial ports."""
        return self.operator.call("GetSerialPorts")

    def GetSerialPortConfiguration(self, SerialPortToken):
        """This operation gets the configuration of a serial port."""
        return self.operator.call(
            "GetSerialPortConfiguration", SerialPortToken=SerialPortToken
        )

    def SetSerialPortConfiguration(self, SerialPortConfiguration, ForcePersistance):
        """Modify a serial port configuration."""
        return self.operator.call(
            "SetSerialPortConfiguration",
            SerialPortConfiguration=SerialPortConfiguration,
            ForcePersistance=ForcePersistance,
        )

    def GetSerialPortConfigurationOptions(self, SerialPortToken):
        """This operation lists what configuration is available for serial ports."""
        return self.operator.call(
            "GetSerialPortConfigurationOptions", SerialPortToken=SerialPortToken
        )

    def SendReceiveSerialCommand(
        self, Token=None, SerialData=None, TimeOut=None, DataLength=None, Delimiter=None
    ):
        """This operation transmitting arbitrary data to the connected serial device and
        then receiving its response data."""
        return self.operator.call(
            "SendReceiveSerialCommand",
            Token=Token,
            SerialData=SerialData,
            TimeOut=TimeOut,
            DataLength=DataLength,
            Delimiter=Delimiter,
        )
