from onvif.services import DeviceIO
from base_service_test import ONVIFServiceTestBase


class TestDeviceIOWSDLCompliance(ONVIFServiceTestBase):
    """Test that DeviceIO service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = DeviceIO
    SERVICE_NAME = "deviceio"
    WSDL_PATH_COMPONENTS = ["ver10", "deviceio.wsdl"]
    BINDING_NAME = "DeviceIOBinding"
    NAMESPACE_PREFIX = "tdc"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/deviceIO/wsdl"
    XADDR_PATH = "/onvif/DeviceIO"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {"method": "GetRelayOutputs"},
            {
                "method": "GetRelayOutputOptions",
                "params": {"RelayOutputToken": "relay1"},
            },
            {
                "method": "SetRelayOutputState",
                "params": {"RelayOutputToken": "relay1", "LogicalState": "active"},
            },
            {"method": "GetAudioSources"},
            {"method": "GetVideoSources"},
            {
                "method": "GetVideoSourceConfiguration",
                "params": {"VideoSourceToken": "video1"},
            },
            {
                "method": "SetVideoSourceConfiguration",
                "params": {
                    "Configuration": {"Token": "video1", "Name": "Config"},
                    "ForcePersistence": True,
                },
            },
            {
                "method": "GetAudioOutputConfiguration",
                "params": {"AudioOutputToken": "audio_out1"},
            },
            {"method": "GetDigitalInputs"},
            {
                "method": "GetDigitalInputConfigurationOptions",
                "params": {"Token": "digital1"},
            },
            {
                "method": "SetDigitalInputConfigurations",
                "params": {
                    "DigitalInputs": [{"Token": "input1", "IdleState": "active"}]
                },
            },
            {"method": "GetSerialPorts"},
            {
                "method": "GetSerialPortConfiguration",
                "params": {"SerialPortToken": "serial1"},
            },
            {
                "method": "SetSerialPortConfiguration",
                "params": {
                    "SerialPortConfiguration": {"Token": "serial1", "BaudRate": 9600},
                    "ForcePersistance": False,
                },
            },
            {
                "method": "SendReceiveSerialCommand",
                "params": {
                    "Token": "serial1",
                    "SerialData": "AT",
                    "TimeOut": 5000,
                    "DataLength": 10,
                    "Delimiter": None,
                },
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetRelayOutputOptions",
                "params": {"RelayOutputToken": "relay_token"},
            },
            {
                "method": "SetRelayOutputState",
                "params": {"RelayOutputToken": "relay1", "LogicalState": "active"},
            },
            {
                "method": "SetRelayOutputSettings",
                "params": {
                    "RelayOutput": {"Token": "relay1"},
                    "RelayOutputToken": "relay1",
                    "Properties": {"Mode": "Monostable"},
                },
            },
            {
                "method": "GetVideoSourceConfiguration",
                "params": {"VideoSourceToken": "video_token"},
            },
            {
                "method": "SetVideoSourceConfiguration",
                "params": {
                    "Configuration": {"Token": "video1", "Bounds": {}},
                    "ForcePersistence": True,
                },
            },
            {
                "method": "GetAudioSourceConfiguration",
                "params": {"AudioSourceToken": "audio_token"},
            },
            {
                "method": "SetAudioOutputConfiguration",
                "params": {
                    "Configuration": {"Token": "audio1", "Volume": 50},
                    "ForcePersistence": False,
                },
            },
            {
                "method": "GetVideoOutputConfigurationOptions",
                "params": {"VideoOutputToken": "video_out_token"},
            },
            {
                "method": "GetDigitalInputConfigurationOptions",
                "params": {"Token": "digital_token"},
            },
            {
                "method": "SetDigitalInputConfigurations",
                "params": {"DigitalInputs": [{"Token": "di1", "IdleState": "closed"}]},
            },
            {
                "method": "GetSerialPortConfiguration",
                "params": {"SerialPortToken": "serial_token"},
            },
            {
                "method": "SetSerialPortConfiguration",
                "params": {
                    "SerialPortConfiguration": {"Token": "sp1", "BaudRate": 115200},
                    "ForcePersistance": True,
                },
            },
            {
                "method": "SendReceiveSerialCommand",
                "params": {
                    "Token": "serial1",
                    "SerialData": "COMMAND",
                    "TimeOut": 10000,
                    "DataLength": 20,
                    "Delimiter": "\r\n",
                },
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
