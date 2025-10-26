from onvif.services import Subscription
from base_service_test import ONVIFServiceTestBase


class TestSubscriptionWSDLCompliance(ONVIFServiceTestBase):
    """Test that Subscription service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Subscription
    SERVICE_NAME = "events.subscription"
    WSDL_PATH_COMPONENTS = ["ver10", "events", "wsdl", "event-vs.wsdl"]
    BINDING_NAME = "SubscriptionManagerBinding"
    NAMESPACE_PREFIX = "wsnt"
    SERVICE_NAMESPACE = "http://docs.oasis-open.org/wsn/bw-2"
    XADDR_PATH = "/onvif/Events"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {
                "method": "Renew",
                "params": {"TerminationTime": "PT2H"},
            },
            {
                "method": "Renew",
                "params": {"TerminationTime": None},
            },
            {
                "method": "Unsubscribe",
                "params": {},
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "Renew",
                "params": {"TerminationTime": "PT3H"},
            },
            {
                "method": "Unsubscribe",
                "params": {},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
