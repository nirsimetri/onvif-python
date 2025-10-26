from onvif.services import Imaging
from base_service_test import ONVIFServiceTestBase


class TestImagingWSDLCompliance(ONVIFServiceTestBase):
    """Test that Imaging service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Imaging
    SERVICE_NAME = "imaging"
    WSDL_PATH_COMPONENTS = ["ver20", "imaging", "wsdl", "imaging.wsdl"]
    BINDING_NAME = "ImagingBinding"
    NAMESPACE_PREFIX = "timg"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver20/imaging/wsdl"
    XADDR_PATH = "/onvif/Imaging"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {
                "method": "GetImagingSettings",
                "params": {"VideoSourceToken": "source1"},
            },
            {
                "method": "SetImagingSettings",
                "params": {
                    "VideoSourceToken": "source2",
                    "ImagingSettings": {"Brightness": 50, "Contrast": 60},
                    "ForcePersistence": True,
                },
            },
            {"method": "GetOptions", "params": {"VideoSourceToken": "source3"}},
            {
                "method": "Move",
                "params": {"VideoSourceToken": "source4", "Focus": {"Absolute": 0.5}},
            },
            {"method": "Stop", "params": {"VideoSourceToken": "source5"}},
            {"method": "GetStatus", "params": {"VideoSourceToken": "source6"}},
            {"method": "GetMoveOptions", "params": {"VideoSourceToken": "source7"}},
            {"method": "GetPresets", "params": {"VideoSourceToken": "source8"}},
            {"method": "GetCurrentPreset", "params": {"VideoSourceToken": "source9"}},
            {
                "method": "SetCurrentPreset",
                "params": {"VideoSourceToken": "source10", "PresetToken": "preset1"},
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetImagingSettings",
                "params": {"VideoSourceToken": "vs1"},
            },
            {
                "method": "SetImagingSettings",
                "params": {
                    "VideoSourceToken": "vs2",
                    "ImagingSettings": {
                        "Brightness": 45,
                        "Contrast": 55,
                        "Saturation": 65,
                    },
                    "ForcePersistence": False,
                },
            },
            {
                "method": "GetOptions",
                "params": {"VideoSourceToken": "vs3"},
            },
            {
                "method": "Move",
                "params": {
                    "VideoSourceToken": "vs4",
                    "Focus": {"Continuous": {"Speed": 0.5}},
                },
            },
            {
                "method": "Stop",
                "params": {"VideoSourceToken": "vs5"},
            },
            {
                "method": "GetStatus",
                "params": {"VideoSourceToken": "vs6"},
            },
            {
                "method": "GetMoveOptions",
                "params": {"VideoSourceToken": "vs7"},
            },
            {
                "method": "GetPresets",
                "params": {"VideoSourceToken": "vs8"},
            },
            {
                "method": "GetCurrentPreset",
                "params": {"VideoSourceToken": "vs9"},
            },
            {
                "method": "SetCurrentPreset",
                "params": {"VideoSourceToken": "vs10", "PresetToken": "preset_token1"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
