from onvif.services import AnalyticsDevice
from base_service_test import ONVIFServiceTestBase


class TestAnalyticsDeviceWSDLCompliance(ONVIFServiceTestBase):
    """Test that AnalyticsDevice service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = AnalyticsDevice
    SERVICE_NAME = "analyticsdevice"
    WSDL_PATH_COMPONENTS = ["ver10", "analyticsdevice.wsdl"]
    BINDING_NAME = "AnalyticsDeviceBinding"
    NAMESPACE_PREFIX = "tad"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/analyticsdevice/wsdl"
    XADDR_PATH = "/onvif/AnalyticsDevice"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {"method": "GetAnalyticsEngines"},
            {
                "method": "GetAnalyticsEngine",
                "params": {"ConfigurationToken": "token123"},
            },
            {"method": "GetAnalyticsEngineControls"},
            {
                "method": "GetAnalyticsEngineControl",
                "params": {"ConfigurationToken": "token456"},
            },
            {
                "method": "CreateAnalyticsEngineControl",
                "params": {"Configuration": {"Token": "config1", "Name": "Control1"}},
            },
            {
                "method": "DeleteAnalyticsEngineControl",
                "params": {"ConfigurationToken": "token789"},
            },
            {
                "method": "SetAnalyticsEngineControl",
                "params": {
                    "SetAnalyticsEngineControl": {"Token": "control1"},
                    "ForcePersistence": True,
                },
            },
            {
                "method": "GetVideoAnalyticsConfiguration",
                "params": {"ConfigurationToken": "va_token"},
            },
            {
                "method": "SetVideoAnalyticsConfiguration",
                "params": {
                    "Configuration": {"Token": "va1", "Name": "Config"},
                    "ForcePersistence": False,
                },
            },
            {"method": "GetAnalyticsEngineInputs"},
            {
                "method": "GetAnalyticsDeviceStreamUri",
                "params": {
                    "StreamSetup": {"Stream": "RTP-Unicast"},
                    "AnalyticsEngineControlToken": "aec123",
                },
            },
            {
                "method": "GetAnalyticsState",
                "params": {"AnalyticsEngineControlToken": "state123"},
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "DeleteAnalyticsEngineControl",
                "params": {"ConfigurationToken": "token123"},
            },
            {
                "method": "CreateAnalyticsEngineControl",
                "params": {"Configuration": {"Token": "config1", "Name": "Control"}},
            },
            {
                "method": "SetAnalyticsEngineControl",
                "params": {
                    "SetAnalyticsEngineControl": {"Token": "control1"},
                    "ForcePersistence": True,
                },
            },
            {
                "method": "GetAnalyticsEngine",
                "params": {"ConfigurationToken": "engine_token"},
            },
            {
                "method": "SetVideoAnalyticsConfiguration",
                "params": {
                    "Configuration": {"Token": "va1", "Name": "Config"},
                    "ForcePersistence": False,
                },
            },
            {
                "method": "SetAnalyticsEngineInput",
                "params": {
                    "Configuration": {"Token": "input1"},
                    "InputToken": "input_token",
                },
            },
            {
                "method": "GetAnalyticsDeviceStreamUri",
                "params": {
                    "StreamSetup": {"Stream": "RTP-Unicast"},
                    "AnalyticsEngineControlToken": "aec_token",
                },
            },
            {
                "method": "CreateAnalyticsEngineInputs",
                "params": {
                    "Configuration": {"Token": "input2"},
                    "ForcePersistence": True,
                },
            },
            {
                "method": "DeleteAnalyticsEngineInputs",
                "params": {"ConfigurationToken": "input_token"},
            },
            {
                "method": "GetAnalyticsState",
                "params": {"AnalyticsEngineControlToken": "state_token"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
