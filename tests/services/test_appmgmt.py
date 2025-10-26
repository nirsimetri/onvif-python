from onvif.services import AppManagement
from base_service_test import ONVIFServiceTestBase


class TestAppManagementWSDLCompliance(ONVIFServiceTestBase):
    """Test that AppManagement service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = AppManagement
    SERVICE_NAME = "appmgmt"
    WSDL_PATH_COMPONENTS = ["ver10", "appmgmt", "wsdl", "appmgmt.wsdl"]
    BINDING_NAME = "AppManagementBinding"
    NAMESPACE_PREFIX = "tam"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/appmgmt/wsdl"
    XADDR_PATH = "/onvif/AppManagement"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {"method": "GetInstalledApps"},
            {"method": "GetAppsInfo", "params": {"AppID": "app123"}},
            {"method": "Activate", "params": {"AppID": "app456"}},
            {"method": "Deactivate", "params": {"AppID": "app789"}},
            {"method": "Uninstall", "params": {"AppID": "app_uninstall"}},
            {
                "method": "InstallLicense",
                "params": {"License": "LICENSE_KEY_123", "AppID": "app_license"},
            },
            {"method": "GetDeviceId"},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "Uninstall",
                "params": {"AppID": "app_to_uninstall"},
            },
            {
                "method": "GetAppsInfo",
                "params": {"AppID": "app_info"},
            },
            {
                "method": "Activate",
                "params": {"AppID": "app_activate"},
            },
            {
                "method": "Deactivate",
                "params": {"AppID": "app_deactivate"},
            },
            {
                "method": "InstallLicense",
                "params": {"License": "LICENSE_123", "AppID": "app_license"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
