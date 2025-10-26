from onvif.services import Events
from base_service_test import ONVIFServiceTestBase


class TestEventsWSDLCompliance(ONVIFServiceTestBase):
    """Test that Events service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Events
    SERVICE_NAME = "events.events"
    WSDL_PATH_COMPONENTS = ["ver10", "events", "wsdl", "event-vs.wsdl"]
    BINDING_NAME = "EventBinding"
    NAMESPACE_PREFIX = "tev"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/events/wsdl"
    XADDR_PATH = "/onvif/Events"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {
                "method": "CreatePullPointSubscription",
                "params": {
                    "Filter": {"TopicExpression": "tns1:Device/Trigger/DigitalInput"},
                    "InitialTerminationTime": "PT1H",
                    "SubscriptionPolicy": {"ChangedOnly": True},
                },
            },
            {"method": "GetEventProperties", "params": {}},
            {
                "method": "AddEventBroker",
                "params": {
                    "EventBroker": {"Address": "http://broker:80", "Type": "MQTT"}
                },
            },
            {"method": "DeleteEventBroker", "params": {"Address": "http://broker:80"}},
            {"method": "GetEventBrokers", "params": {"Address": "http://broker:80"}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "CreatePullPointSubscription",
                "params": {
                    "Filter": {"TopicExpression": "tns1:VideoSource/MotionAlarm"},
                    "InitialTerminationTime": "PT30M",
                    "SubscriptionPolicy": {"ChangedOnly": False},
                },
            },
            {
                "method": "AddEventBroker",
                "params": {
                    "EventBroker": {
                        "Address": "http://test-broker:8080",
                        "Type": "HTTP",
                    }
                },
            },
            {
                "method": "DeleteEventBroker",
                "params": {"Address": "http://test-broker:8080"},
            },
            {
                "method": "GetEventBrokers",
                "params": {"Address": "http://broker-query:9090"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
