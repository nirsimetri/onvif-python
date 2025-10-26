from onvif.services import Display
from base_service_test import ONVIFServiceTestBase


class TestDisplayWSDLCompliance(ONVIFServiceTestBase):
    """Test that Display service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = Display
    SERVICE_NAME = "display"
    WSDL_PATH_COMPONENTS = ["ver10", "display.wsdl"]
    BINDING_NAME = "DisplayBinding"
    NAMESPACE_PREFIX = "tls"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/display/wsdl"
    XADDR_PATH = "/onvif/Display"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {"method": "GetLayout", "params": {"VideoOutput": "output1"}},
            {
                "method": "SetLayout",
                "params": {"VideoOutput": "output1", "Layout": {"PaneLayout": "1x1"}},
            },
            {"method": "GetDisplayOptions", "params": {"VideoOutput": "output2"}},
            {"method": "GetPaneConfigurations", "params": {"VideoOutput": "output3"}},
            {
                "method": "GetPaneConfiguration",
                "params": {"VideoOutput": "output1", "Pane": "pane1"},
            },
            {
                "method": "SetPaneConfigurations",
                "params": {
                    "VideoOutput": "output1",
                    "PaneConfiguration": {
                        "Token": "pane1",
                        "VideoSourceToken": "source1",
                    },
                },
            },
            {
                "method": "SetPaneConfiguration",
                "params": {
                    "VideoOutput": "output2",
                    "PaneConfiguration": {
                        "Token": "pane2",
                        "VideoSourceToken": "source2",
                    },
                },
            },
            {
                "method": "CreatePaneConfiguration",
                "params": {
                    "VideoOutput": "output3",
                    "PaneConfiguration": {
                        "Token": "new_pane",
                        "VideoSourceToken": "source3",
                    },
                },
            },
            {
                "method": "DeletePaneConfiguration",
                "params": {"VideoOutput": "output4", "PaneToken": "pane_delete"},
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetLayout",
                "params": {"VideoOutput": "vo1"},
            },
            {
                "method": "SetLayout",
                "params": {"VideoOutput": "vo2", "Layout": {"PaneLayout": "2x2"}},
            },
            {
                "method": "GetDisplayOptions",
                "params": {"VideoOutput": "vo3"},
            },
            {
                "method": "GetPaneConfigurations",
                "params": {"VideoOutput": "vo4"},
            },
            {
                "method": "GetPaneConfiguration",
                "params": {"VideoOutput": "vo5", "Pane": "pane5"},
            },
            {
                "method": "SetPaneConfigurations",
                "params": {
                    "VideoOutput": "vo6",
                    "PaneConfiguration": {"Token": "pane6", "VideoSourceToken": "vs6"},
                },
            },
            {
                "method": "SetPaneConfiguration",
                "params": {
                    "VideoOutput": "vo7",
                    "PaneConfiguration": {"Token": "pane7", "VideoSourceToken": "vs7"},
                },
            },
            {
                "method": "CreatePaneConfiguration",
                "params": {
                    "VideoOutput": "vo8",
                    "PaneConfiguration": {
                        "Token": "new_pane8",
                        "VideoSourceToken": "vs8",
                    },
                },
            },
            {
                "method": "DeletePaneConfiguration",
                "params": {"VideoOutput": "vo9", "PaneToken": "pane_to_delete"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
