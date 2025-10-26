# onvif/services/analytics/ruleengine.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class RuleEngine(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.41 (December 2013) Release Notes
        # - RuleEngineBinding (ver20/analytics/wsdl/analytics.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/wsdl/analytics.wsdl

        definition = ONVIFWSDL.get_definition("ruleengine", "ver20")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Analytics",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetSupportedRules(self, ConfigurationToken):
        return self.operator.call(
            "GetSupportedRules", ConfigurationToken=ConfigurationToken
        )

    def CreateRules(self, ConfigurationToken, Rule):
        return self.operator.call(
            "CreateRules", ConfigurationToken=ConfigurationToken, Rule=Rule
        )

    def DeleteRules(self, ConfigurationToken, RuleName):
        return self.operator.call(
            "DeleteRules", ConfigurationToken=ConfigurationToken, RuleName=RuleName
        )

    def GetRules(self, ConfigurationToken):
        return self.operator.call("GetRules", ConfigurationToken=ConfigurationToken)

    def GetRuleOptions(self, ConfigurationToken, RuleType=None):
        return self.operator.call(
            "GetRuleOptions", RuleType=RuleType, ConfigurationToken=ConfigurationToken
        )

    def ModifyRules(self, ConfigurationToken, Rule):
        return self.operator.call(
            "ModifyRules", ConfigurationToken=ConfigurationToken, Rule=Rule
        )
