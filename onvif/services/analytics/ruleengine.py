"""Analytics (RuleEngine) service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class RuleEngine(ONVIFService):
    """Analytics (RuleEngine) service client.

    References:
        - First introduced: ONVIF Release 2.41 (December 2013)
        - Binding name: `RuleEngineBinding` (ver20/analytics/wsdl/analytics.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/wsdl/analytics.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Analytics.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("ruleengine", "ver20")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Analytics",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetSupportedRules(self, ConfigurationToken):
        """List all rules that are supported by the given
        VideoAnalyticsConfiguration."""
        return self.operator.call(
            "GetSupportedRules", ConfigurationToken=ConfigurationToken
        )

    def CreateRules(self, ConfigurationToken, Rule):
        """Add one or more rules to an existing VideoAnalyticsConfiguration.

        The available supported types can be retrieved via GetSupportedRules, where the
        Name of the supported rule correspond to the type of an rule instance.

        Pass unique module names which can be later used as reference. The Parameters of
        the rules must match those of the corresponding description.

        Although this method is mandatory a device implementation must not support
        adding rules. Instead it can provide a fixed set of predefined configurations
        via the media service function GetCompatibleVideoAnalyticsConfigurations.
        """
        return self.operator.call(
            "CreateRules", ConfigurationToken=ConfigurationToken, Rule=Rule
        )

    def DeleteRules(self, ConfigurationToken, RuleName):
        """Remove one or more rules from a VideoAnalyticsConfiguration."""
        return self.operator.call(
            "DeleteRules", ConfigurationToken=ConfigurationToken, RuleName=RuleName
        )

    def GetRules(self, ConfigurationToken):
        """List the currently assigned set of rules of a VideoAnalyticsConfiguration."""
        return self.operator.call("GetRules", ConfigurationToken=ConfigurationToken)

    def GetRuleOptions(self, ConfigurationToken, RuleType=None):
        """Return the options for the supported rules that specify an Option
        attribute."""
        return self.operator.call(
            "GetRuleOptions", RuleType=RuleType, ConfigurationToken=ConfigurationToken
        )

    def ModifyRules(self, ConfigurationToken, Rule):
        """Modify one or more rules of a VideoAnalyticsConfiguration.

        The rules are referenced by their names.
        """
        return self.operator.call(
            "ModifyRules", ConfigurationToken=ConfigurationToken, Rule=Rule
        )
