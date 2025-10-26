# onvif/services/deviceio.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class DeviceIO(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.1 (June 2011) Split from Core 2.0
        # - DeviceIOBinding (ver10/deviceio.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/deviceio.wsdl

        definition = ONVIFWSDL.get_definition("deviceio")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="DeviceIO",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetRelayOutputOptions(self, RelayOutputToken=None):
        return self.operator.call(
            "GetRelayOutputOptions", RelayOutputToken=RelayOutputToken
        )

    def GetAudioSources(self):
        return self.operator.call("GetAudioSources")

    def GetAudioOutputs(self):
        return self.operator.call("GetAudioOutputs")

    def GetVideoSources(self):
        return self.operator.call("GetVideoSources")

    def GetVideoOutputs(self):
        return self.operator.call("GetVideoOutputs")

    def GetVideoSourceConfiguration(self, VideoSourceToken):
        return self.operator.call(
            "GetVideoSourceConfiguration", VideoSourceToken=VideoSourceToken
        )

    def GetVideoOutputConfiguration(self, VideoOutputToken):
        return self.operator.call(
            "GetVideoOutputConfiguration", VideoOutputToken=VideoOutputToken
        )

    def GetAudioSourceConfiguration(self, AudioSourceToken):
        return self.operator.call(
            "GetAudioSourceConfiguration", AudioSourceToken=AudioSourceToken
        )

    def GetAudioOutputConfiguration(self, AudioOutputToken):
        return self.operator.call(
            "GetAudioOutputConfiguration", AudioOutputToken=AudioOutputToken
        )

    def SetVideoSourceConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetVideoSourceConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetVideoOutputConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetVideoOutputConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioSourceConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetAudioSourceConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAudioOutputConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetAudioOutputConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def GetVideoSourceConfigurationOptions(self, VideoSourceToken):
        return self.operator.call(
            "GetVideoSourceConfigurationOptions", VideoSourceToken=VideoSourceToken
        )

    def GetVideoOutputConfigurationOptions(self, VideoOutputToken):
        return self.operator.call(
            "GetVideoOutputConfigurationOptions", VideoOutputToken=VideoOutputToken
        )

    def GetAudioSourceConfigurationOptions(self, AudioSourceToken):
        return self.operator.call(
            "GetAudioSourceConfigurationOptions", AudioSourceToken=AudioSourceToken
        )

    def GetAudioOutputConfigurationOptions(self, AudioOutputToken):
        return self.operator.call(
            "GetAudioOutputConfigurationOptions", AudioOutputToken=AudioOutputToken
        )

    def GetRelayOutputs(self):
        return self.operator.call("GetRelayOutputs")

    def SetRelayOutputSettings(self, RelayOutput, RelayOutputToken, Properties):
        return self.operator.call(
            "SetRelayOutputSettings",
            RelayOutput=RelayOutput,
            RelayOutputToken=RelayOutputToken,
            Properties=Properties,
        )

    def SetRelayOutputState(self, RelayOutputToken, LogicalState):
        return self.operator.call(
            "SetRelayOutputState",
            RelayOutputToken=RelayOutputToken,
            LogicalState=LogicalState,
        )

    def GetDigitalInputs(self):
        return self.operator.call("GetDigitalInputs")

    def GetDigitalInputConfigurationOptions(self, Token=None):
        return self.operator.call("GetDigitalInputConfigurationOptions", Token=Token)

    def SetDigitalInputConfigurations(self, DigitalInputs):
        return self.operator.call(
            "SetDigitalInputConfigurations", DigitalInputs=DigitalInputs
        )

    def GetSerialPorts(self):
        return self.operator.call("GetSerialPorts")

    def GetSerialPortConfiguration(self, SerialPortToken):
        return self.operator.call(
            "GetSerialPortConfiguration", SerialPortToken=SerialPortToken
        )

    def SetSerialPortConfiguration(self, SerialPortConfiguration, ForcePersistance):
        return self.operator.call(
            "SetSerialPortConfiguration",
            SerialPortConfiguration=SerialPortConfiguration,
            ForcePersistance=ForcePersistance,
        )

    def GetSerialPortConfigurationOptions(self, SerialPortToken):
        return self.operator.call(
            "GetSerialPortConfigurationOptions", SerialPortToken=SerialPortToken
        )

    def SendReceiveSerialCommand(
        self, Token=None, SerialData=None, TimeOut=None, DataLength=None, Delimiter=None
    ):
        return self.operator.call(
            "SendReceiveSerialCommand",
            Token=Token,
            SerialData=SerialData,
            TimeOut=TimeOut,
            DataLength=DataLength,
            Delimiter=Delimiter,
        )
