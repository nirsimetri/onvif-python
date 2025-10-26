from onvif.services import Receiver
from base_service_test import ONVIFServiceTestBase


class TestReceiverWSDLCompliance(ONVIFServiceTestBase):
    """Test that Receiver service implementation matches WSDL specification."""

    # Service configuration
    SERVICE_CLASS = Receiver
    SERVICE_NAME = "receiver"
    WSDL_PATH_COMPONENTS = ["ver10", "receiver.wsdl"]
    BINDING_NAME = "ReceiverBinding"
    NAMESPACE_PREFIX = "trv"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/receiver/wsdl"
    XADDR_PATH = "/onvif/Receiver"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {"method": "GetReceivers", "params": {}},
            {"method": "GetReceiver", "params": {"ReceiverToken": "receiver1"}},
            {
                "method": "CreateReceiver",
                "params": {
                    "Configuration": {
                        "Mode": "AutoConnect",
                        "MediaUri": "rtsp://example.com/stream",
                    }
                },
            },
            {"method": "DeleteReceiver", "params": {"ReceiverToken": "receiver2"}},
            {
                "method": "ConfigureReceiver",
                "params": {
                    "ReceiverToken": "receiver3",
                    "Configuration": {
                        "Mode": "NeverConnect",
                        "MediaUri": "rtsp://test.com/video",
                    },
                },
            },
            {
                "method": "SetReceiverMode",
                "params": {"ReceiverToken": "receiver4", "Mode": "AlwaysConnect"},
            },
            {"method": "GetReceiverState", "params": {"ReceiverToken": "receiver5"}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetReceiver",
                "params": {"ReceiverToken": "rcv1"},
            },
            {
                "method": "CreateReceiver",
                "params": {
                    "Configuration": {
                        "Mode": "AutoConnect",
                        "MediaUri": "rtsp://192.168.1.100/stream",
                    }
                },
            },
            {
                "method": "DeleteReceiver",
                "params": {"ReceiverToken": "rcv2"},
            },
            {
                "method": "ConfigureReceiver",
                "params": {
                    "ReceiverToken": "rcv3",
                    "Configuration": {
                        "Mode": "NeverConnect",
                        "MediaUri": "rtsp://10.0.0.50/video1",
                    },
                },
            },
            {
                "method": "SetReceiverMode",
                "params": {"ReceiverToken": "rcv4", "Mode": "AlwaysConnect"},
            },
            {
                "method": "GetReceiverState",
                "params": {"ReceiverToken": "rcv5"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
