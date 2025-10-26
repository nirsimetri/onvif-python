from onvif.services import RuleEngine
from base_service_test import ONVIFServiceTestBase


class TestRuleEngineWSDLCompliance(ONVIFServiceTestBase):
    """Test that RuleEngine service implementation matches WSDL specification."""

    # Service configuration
    SERVICE_CLASS = RuleEngine
    SERVICE_NAME = "analytics.ruleengine"
    WSDL_PATH_COMPONENTS = ["ver20", "analytics", "wsdl", "analytics.wsdl"]
    BINDING_NAME = "RuleEngineBinding"
    NAMESPACE_PREFIX = "tan"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver20/analytics/wsdl"
    XADDR_PATH = "/onvif/Analytics"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {
                "method": "GetSupportedRules",
                "params": {"ConfigurationToken": "config_token_1"},
            },
            {
                "method": "CreateRules",
                "params": {
                    "ConfigurationToken": "config_token_2",
                    "Rule": {"Name": "rule1", "Type": "LineDetector"},
                },
            },
            {
                "method": "DeleteRules",
                "params": {"ConfigurationToken": "config_token_3", "RuleName": "rule1"},
            },
            {"method": "GetRules", "params": {"ConfigurationToken": "config_token_4"}},
            {
                "method": "GetRuleOptions",
                "params": {
                    "RuleType": "CellMotionDetector",
                    "ConfigurationToken": "config_token_5",
                },
            },
            {
                "method": "GetRuleOptions",
                "params": {"RuleType": None, "ConfigurationToken": "config_token_6"},
            },
            {
                "method": "ModifyRules",
                "params": {
                    "ConfigurationToken": "config_token_7",
                    "Rule": {"Name": "rule1", "Type": "LineDetector", "Parameters": {}},
                },
            },
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetSupportedRules",
                "params": {"ConfigurationToken": "token123"},
            },
            {
                "method": "CreateRules",
                "params": {
                    "ConfigurationToken": "token123",
                    "Rule": {"Name": "TestRule", "Type": "MotionDetector"},
                },
            },
            {
                "method": "DeleteRules",
                "params": {"ConfigurationToken": "token123", "RuleName": "TestRule"},
            },
            {
                "method": "GetRules",
                "params": {"ConfigurationToken": "token123"},
            },
            {
                "method": "GetRuleOptions",
                "params": {
                    "ConfigurationToken": "token123",
                    "RuleType": "LineDetector",
                },
            },
            {
                "method": "ModifyRules",
                "params": {
                    "ConfigurationToken": "token123",
                    "Rule": {"Name": "TestRule", "Type": "MotionDetector"},
                },
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
