from onvif.services import Thermal
from base_service_test import ONVIFServiceTestBase


class TestThermalWSDLCompliance(ONVIFServiceTestBase):
    """Test that Thermal service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Thermal
    SERVICE_NAME = "thermal"
    WSDL_PATH_COMPONENTS = ["ver10", "thermal", "wsdl", "thermal.wsdl"]
    BINDING_NAME = "ThermalBinding"
    NAMESPACE_PREFIX = "tth"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/thermal/wsdl"
    XADDR_PATH = "/onvif/Thermal"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {
                "method": "GetConfigurationOptions",
                "params": {"VideoSourceToken": "source1"},
            },
            {
                "method": "GetConfiguration",
                "params": {"VideoSourceToken": "source2"},
            },
            {"method": "GetConfigurations", "params": {}},
            {
                "method": "SetConfiguration",
                "params": {
                    "VideoSourceToken": "source3",
                    "Configuration": {"ColorPalette": "WhiteHot", "NUCTable": "Table1"},
                },
            },
            {
                "method": "GetRadiometryConfigurationOptions",
                "params": {"VideoSourceToken": "source4"},
            },
            {
                "method": "GetRadiometryConfiguration",
                "params": {"VideoSourceToken": "source5"},
            },
            {
                "method": "SetRadiometryConfiguration",
                "params": {
                    "VideoSourceToken": "source6",
                    "Configuration": {
                        "ReflectedAmbientTemperature": 20.0,
                        "Emissivity": 0.95,
                    },
                },
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetConfigurationOptions",
                "params": {"VideoSourceToken": "vs1"},
            },
            {
                "method": "GetConfiguration",
                "params": {"VideoSourceToken": "vs2"},
            },
            {
                "method": "SetConfiguration",
                "params": {
                    "VideoSourceToken": "vs3",
                    "Configuration": {"ColorPalette": "BlackHot"},
                },
            },
            {
                "method": "GetRadiometryConfigurationOptions",
                "params": {"VideoSourceToken": "vs4"},
            },
            {
                "method": "GetRadiometryConfiguration",
                "params": {"VideoSourceToken": "vs5"},
            },
            {
                "method": "SetRadiometryConfiguration",
                "params": {
                    "VideoSourceToken": "vs6",
                    "Configuration": {"Emissivity": 0.98},
                },
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
