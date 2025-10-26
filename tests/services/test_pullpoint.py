from onvif.services import PullPoint
from base_service_test import ONVIFServiceTestBase


class TestPullPointWSDLCompliance(ONVIFServiceTestBase):
    """Test that PullPoint service implementation matches WSDL specification."""

    # Service configuration
    SERVICE_CLASS = PullPoint
    SERVICE_NAME = "events.pullpoint"
    WSDL_PATH_COMPONENTS = ["ver10", "events", "wsdl", "event-vs.wsdl"]
    BINDING_NAME = "PullPointSubscriptionBinding"
    NAMESPACE_PREFIX = "tev"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/events/wsdl"
    XADDR_PATH = "/onvif/Events"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {
                "method": "PullMessages",
                "params": {"Timeout": "PT1M", "MessageLimit": 10},
            },
            {
                "method": "Seek",
                "params": {"UtcTime": "2024-01-01T00:00:00Z", "Reverse": None},
            },
            {
                "method": "Seek",
                "params": {"UtcTime": "2024-01-01T12:00:00Z", "Reverse": True},
            },
            {"method": "SetSynchronizationPoint", "params": {}},
            {"method": "Unsubscribe", "params": {}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "PullMessages",
                "params": {"Timeout": "PT30S", "MessageLimit": 100},
            },
            {
                "method": "Seek",
                "params": {"UtcTime": "2024-06-15T10:30:00Z", "Reverse": False},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)

    def test_pullpoint_operations_count(self):
        """Informational test to show the number of PullPoint operations."""
        wsdl_operations = self.get_wsdl_operations()
        implemented_methods = self.get_implemented_methods()

        print(
            f"\nPullPoint WSDL contains {len(wsdl_operations)} operations, "
            f"{len(implemented_methods)} methods implemented"
        )
