from onvif.services import Replay
from base_service_test import ONVIFServiceTestBase


class TestReplayWSDLCompliance(ONVIFServiceTestBase):
    """Test that Replay service implementation matches WSDL specification."""

    # Service configuration
    SERVICE_CLASS = Replay
    SERVICE_NAME = "replay"
    WSDL_PATH_COMPONENTS = ["ver10", "replay.wsdl"]
    BINDING_NAME = "ReplayBinding"
    NAMESPACE_PREFIX = "trp"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/replay/wsdl"
    XADDR_PATH = "/onvif/Replay"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {
                "method": "GetReplayUri",
                "params": {
                    "StreamSetup": {
                        "Stream": "RTP-Unicast",
                        "Transport": {"Protocol": "RTSP"},
                    },
                    "RecordingToken": "recording1",
                },
            },
            {"method": "GetReplayConfiguration", "params": {}},
            {
                "method": "SetReplayConfiguration",
                "params": {"Configuration": {"SessionTimeout": "PT1H"}},
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetReplayUri",
                "params": {
                    "StreamSetup": {
                        "Stream": "RTP-Multicast",
                        "Transport": {"Protocol": "HTTP"},
                    },
                    "RecordingToken": "rec1",
                },
            },
            {
                "method": "SetReplayConfiguration",
                "params": {"Configuration": {"SessionTimeout": "PT30M"}},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
