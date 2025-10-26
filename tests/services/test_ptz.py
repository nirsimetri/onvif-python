from onvif.services import PTZ
from base_service_test import ONVIFServiceTestBase


class TestPTZWSDLCompliance(ONVIFServiceTestBase):
    """Test that PTZ service implementation matches WSDL specification."""

    # Service configuration
    SERVICE_CLASS = PTZ
    SERVICE_NAME = "ptz"
    WSDL_PATH_COMPONENTS = ["ver20", "ptz", "wsdl", "ptz.wsdl"]
    BINDING_NAME = "PTZBinding"
    NAMESPACE_PREFIX = "tptz"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver20/ptz/wsdl"
    XADDR_PATH = "/onvif/PTZ"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {"method": "GetConfigurations", "params": {}},
            {"method": "GetNodes", "params": {}},
            {"method": "GetStatus", "params": {"ProfileToken": "profile1"}},
            {"method": "GetPresets", "params": {"ProfileToken": "profile2"}},
            {
                "method": "SetPreset",
                "params": {
                    "ProfileToken": "profile3",
                    "PresetName": "Home",
                    "PresetToken": "preset1",
                },
            },
            {
                "method": "GotoPreset",
                "params": {
                    "ProfileToken": "profile4",
                    "PresetToken": "preset2",
                    "Speed": {"PanTilt": {"x": 0.5, "y": 0.5}},
                },
            },
            {
                "method": "AbsoluteMove",
                "params": {
                    "ProfileToken": "profile5",
                    "Position": {"PanTilt": {"x": 0.0, "y": 0.0}, "Zoom": {"x": 1.0}},
                    "Speed": {"PanTilt": {"x": 1.0, "y": 1.0}},
                },
            },
            {
                "method": "RelativeMove",
                "params": {
                    "ProfileToken": "profile6",
                    "Translation": {"PanTilt": {"x": 0.1, "y": 0.1}},
                    "Speed": {"PanTilt": {"x": 0.5, "y": 0.5}},
                },
            },
            {
                "method": "ContinuousMove",
                "params": {
                    "ProfileToken": "profile7",
                    "Velocity": {"PanTilt": {"x": 0.5, "y": 0.0}},
                    "Timeout": "PT5S",
                },
            },
            {
                "method": "Stop",
                "params": {"ProfileToken": "profile8", "PanTilt": True, "Zoom": False},
            },
            {
                "method": "SetConfiguration",
                "params": {
                    "PTZConfiguration": {"Token": "config1", "NodeToken": "node1"},
                    "ForcePersistence": True,
                },
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetStatus",
                "params": {"ProfileToken": "prof1"},
            },
            {
                "method": "GetPresets",
                "params": {"ProfileToken": "prof2"},
            },
            {
                "method": "SetPreset",
                "params": {
                    "ProfileToken": "prof3",
                    "PresetName": "Position1",
                    "PresetToken": "preset1",
                },
            },
            {
                "method": "GotoPreset",
                "params": {
                    "ProfileToken": "prof4",
                    "PresetToken": "preset2",
                    "Speed": {"PanTilt": {"x": 0.8, "y": 0.8}},
                },
            },
            {
                "method": "AbsoluteMove",
                "params": {
                    "ProfileToken": "prof5",
                    "Position": {"PanTilt": {"x": 0.5, "y": 0.5}},
                    "Speed": {"PanTilt": {"x": 0.6, "y": 0.6}},
                },
            },
            {
                "method": "RelativeMove",
                "params": {
                    "ProfileToken": "prof6",
                    "Translation": {"PanTilt": {"x": 0.2, "y": -0.1}},
                    "Speed": {"PanTilt": {"x": 0.3, "y": 0.3}},
                },
            },
            {
                "method": "ContinuousMove",
                "params": {
                    "ProfileToken": "prof7",
                    "Velocity": {"PanTilt": {"x": 0.4, "y": 0.0}},
                    "Timeout": "PT10S",
                },
            },
            {
                "method": "Stop",
                "params": {"ProfileToken": "prof8", "PanTilt": True, "Zoom": True},
            },
            {
                "method": "SetConfiguration",
                "params": {
                    "PTZConfiguration": {"Token": "config1"},
                    "ForcePersistence": False,
                },
            },
            {
                "method": "GotoHomePosition",
                "params": {
                    "ProfileToken": "prof9",
                    "Speed": {"PanTilt": {"x": 1.0, "y": 1.0}},
                },
            },
            {
                "method": "RemovePreset",
                "params": {"ProfileToken": "prof10", "PresetToken": "preset3"},
            },
            {
                "method": "GetPresetTours",
                "params": {"ProfileToken": "prof11"},
            },
            {
                "method": "CreatePresetTour",
                "params": {"ProfileToken": "prof12"},
            },
            {
                "method": "SendAuxiliaryCommand",
                "params": {"ProfileToken": "prof13", "AuxiliaryData": "command1"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
