from onvif.services import Notification
from base_service_test import ONVIFServiceTestBase


class TestNotificationWSDLCompliance(ONVIFServiceTestBase):
    """Test that Notification service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Notification
    SERVICE_NAME = "events.notification"
    WSDL_PATH_COMPONENTS = ["ver10", "events", "wsdl", "event-vs.wsdl"]
    BINDING_NAME = "NotificationProducerBinding"
    NAMESPACE_PREFIX = "tev"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/events/wsdl"
    XADDR_PATH = "/onvif/Events"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {
                "method": "Subscribe",
                "params": {
                    "ConsumerReference": {"Address": "http://consumer:8080/notify"},
                    "Filter": {"TopicExpression": "tns1:Device/Trigger/DigitalInput"},
                    "InitialTerminationTime": "PT1H",
                    "SubscriptionPolicy": {"ChangedOnly": True},
                },
            },
            {
                "method": "Subscribe",
                "params": {
                    "ConsumerReference": None,
                    "Filter": None,
                    "InitialTerminationTime": None,
                    "SubscriptionPolicy": None,
                },
            },
            {
                "method": "GetCurrentMessage",
                "params": {"Topic": "tns1:VideoSource/MotionAlarm"},
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "Subscribe",
                "params": {
                    "ConsumerReference": {
                        "Address": "http://test-consumer:9090/callback"
                    },
                    "Filter": {"TopicExpression": "tns1:RuleEngine/CellMotionDetector"},
                    "InitialTerminationTime": "PT30M",
                    "SubscriptionPolicy": {"ChangedOnly": False},
                },
            },
            {
                "method": "GetCurrentMessage",
                "params": {"Topic": "tns1:Device/HardwareFailure/StorageFailure"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)

    def test_notification_operations_count(self):
        """Informational test to show the number of Notification operations."""
        wsdl_operations = self.get_wsdl_operations()
        implemented_methods = self.get_implemented_methods()

        print(
            f"\nNotification WSDL contains {len(wsdl_operations)} operations, "
            f"{len(implemented_methods)} methods implemented"
        )
