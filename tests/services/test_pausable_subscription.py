from onvif.services import PausableSubscription
from base_service_test import ONVIFServiceTestBase


class TestPausableSubscriptionWSDLCompliance(ONVIFServiceTestBase):
    """Test that PausableSubscription service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = PausableSubscription
    SERVICE_NAME = "events.pausable_subscription"
    WSDL_PATH_COMPONENTS = ["ver10", "events", "wsdl", "event-vs.wsdl"]
    BINDING_NAME = "PausableSubscriptionManagerBinding"
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
            {
                "method": "PauseSubscription",
                "params": {},
            },
            {
                "method": "ResumeSubscription",
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
                "method": "Renew",
                "params": {"TerminationTime": None},
            },
            {
                "method": "Unsubscribe",
                "params": {},
            },
            {
                "method": "PauseSubscription",
                "params": {},
            },
            {
                "method": "ResumeSubscription",
                "params": {},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)

    def test_pausable_subscription_methods(self):
        """Test that PausableSubscription has the correct methods."""
        # Check that all required methods exist
        assert hasattr(PausableSubscription, "Renew")
        assert hasattr(PausableSubscription, "Unsubscribe")
        assert hasattr(PausableSubscription, "PauseSubscription")
        assert hasattr(PausableSubscription, "ResumeSubscription")

        # Check that methods are callable
        assert callable(getattr(PausableSubscription, "Renew"))
        assert callable(getattr(PausableSubscription, "Unsubscribe"))
        assert callable(getattr(PausableSubscription, "PauseSubscription"))
        assert callable(getattr(PausableSubscription, "ResumeSubscription"))

    def test_inheritance(self):
        """Test that PausableSubscription inherits from ONVIFService."""
        from onvif.utils import ONVIFService

        assert issubclass(PausableSubscription, ONVIFService)

    def test_pause_resume_operations(self):
        """Test pause and resume operations specific to PausableSubscription."""
        # These are the unique operations that differentiate PausableSubscription
        # from regular Subscription
        implemented_methods = self.get_implemented_methods()

        # Ensure pause/resume methods are implemented
        assert (
            "PauseSubscription" in implemented_methods
        ), "PauseSubscription method should be implemented"
        assert (
            "ResumeSubscription" in implemented_methods
        ), "ResumeSubscription method should be implemented"

        # Ensure they have no parameters (according to WSDL)
        pause_params = implemented_methods["PauseSubscription"]["params"]
        resume_params = implemented_methods["ResumeSubscription"]["params"]

        assert len(pause_params) == 0, "PauseSubscription should have no parameters"
        assert len(resume_params) == 0, "ResumeSubscription should have no parameters"
