from onvif.services import Device
from base_service_test import ONVIFServiceTestBase


class TestDeviceMgmtWSDLCompliance(ONVIFServiceTestBase):
    """Test that Device service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Device
    SERVICE_NAME = "devicemgmt"
    WSDL_PATH_COMPONENTS = ["ver10", "device", "wsdl", "devicemgmt.wsdl"]
    BINDING_NAME = "DeviceBinding"
    NAMESPACE_PREFIX = "tds"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/device/wsdl"
    XADDR_PATH = "/onvif/device_service"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetDeviceInformation"},
            {"method": "GetSystemDateAndTime"},
            {"method": "GetServices", "params": {"IncludeCapability": True}},
            {
                "method": "SetSystemDateAndTime",
                "params": {
                    "DateTimeType": "Manual",
                    "DaylightSavings": False,
                    "TimeZone": {"TZ": "UTC"},
                    "UTCDateTime": None,
                },
            },
            {"method": "GetCapabilities", "params": {"Category": "All"}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "CreateUsers",
                "params": {"User": [{"Username": "test", "Password": "pass"}]},
            },
            {"method": "DeleteUsers", "params": {"Username": ["test"]}},
            {"method": "SetHostname", "params": {"Name": "camera1"}},
            {"method": "GetSystemLog", "params": {"LogType": "System"}},
            {
                "method": "SetDNS",
                "params": {
                    "FromDHCP": False,
                    "SearchDomain": ["example.com"],
                    "DNSManual": None,
                },
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
