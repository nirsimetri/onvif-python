from onvif.services import Analytics
from base_service_test import ONVIFServiceTestBase


class TestAnalyticsWSDLCompliance(ONVIFServiceTestBase):
    """Test that Analytics service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Analytics
    SERVICE_NAME = "analytics.analytics"
    WSDL_PATH_COMPONENTS = ["ver20", "analytics", "wsdl", "analytics.wsdl"]
    BINDING_NAME = "AnalyticsEngineBinding"
    NAMESPACE_PREFIX = "tan"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver20/analytics/wsdl"
    XADDR_PATH = "/onvif/Analytics"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {
                "method": "GetSupportedAnalyticsModules",
                "params": {"ConfigurationToken": "token1"},
            },
            {
                "method": "CreateAnalyticsModules",
                "params": {
                    "ConfigurationToken": "token1",
                    "AnalyticsModule": {"Name": "module1"},
                },
            },
            {
                "method": "GetAnalyticsModuleOptions",
                "params": {"ConfigurationToken": "token1", "Type": "SomeType"},
            },
            {"method": "GetSupportedMetadata", "params": {"Type": "MetadataType"}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetAnalyticsModules",
                "params": {"ConfigurationToken": "token123"},
            },
            {
                "method": "DeleteAnalyticsModules",
                "params": {
                    "ConfigurationToken": "token123",
                    "AnalyticsModuleName": "module1",
                },
            },
            {
                "method": "ModifyAnalyticsModules",
                "params": {
                    "ConfigurationToken": "token123",
                    "AnalyticsModule": {"Name": "module1", "Type": "Type1"},
                },
            },
            {
                "method": "GetAnalyticsModuleOptions",
                "params": {"ConfigurationToken": "token123", "Type": "Type1"},
            },
            {
                "method": "GetSupportedMetadata",
                "params": {"Type": "MetadataType"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
