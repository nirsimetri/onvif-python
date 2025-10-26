from onvif.services import ActionEngine
from base_service_test import ONVIFServiceTestBase


class TestActionEngineWSDLCompliance(ONVIFServiceTestBase):
    """Test that ActionEngine service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = ActionEngine
    SERVICE_NAME = "actionengine"
    WSDL_PATH_COMPONENTS = ["ver10", "actionengine.wsdl"]
    BINDING_NAME = "ActionEngineBinding"
    NAMESPACE_PREFIX = "tae"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/actionengine/wsdl"
    XADDR_PATH = "/onvif/ActionEngine"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {"method": "GetSupportedActions"},
            {"method": "GetActions"},
            {
                "method": "CreateActions",
                "params": {"Action": {"Token": "action1", "Name": "Action1"}},
            },
            {"method": "DeleteActions", "params": {"Token": "token123"}},
            {
                "method": "ModifyActions",
                "params": {"Action": {"Token": "action1", "Name": "Modified Action"}},
            },
            {"method": "GetActionTriggers"},
            {
                "method": "CreateActionTriggers",
                "params": {"ActionTrigger": {"Token": "trigger1", "Name": "Trigger1"}},
            },
            {"method": "DeleteActionTriggers", "params": {"Token": "token456"}},
            {
                "method": "ModifyActionTriggers",
                "params": {
                    "ActionTrigger": {"Token": "trigger1", "Name": "Modified Trigger"}
                },
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "CreateActions",
                "params": {"Action": {"Token": "action1", "Name": "New Action"}},
            },
            {
                "method": "DeleteActions",
                "params": {"Token": "token123"},
            },
            {
                "method": "ModifyActions",
                "params": {
                    "Action": {
                        "Token": "action1",
                        "Name": "Updated Action",
                    }
                },
            },
            {
                "method": "CreateActionTriggers",
                "params": {"ActionTrigger": {"Token": "trigger1", "Name": "Trigger"}},
            },
            {
                "method": "DeleteActionTriggers",
                "params": {"Token": "trigger123"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
