# onvif/services/analytics/analytics.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class Analytics(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.41 (December 2013) Release Notes
        # - AnalyticsEngineBinding (ver20/analytics/wsdl/analytics.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/wsdl/analytics.wsdl

        definition = ONVIFWSDL.get_definition("analytics", "ver20")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Analytics",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetSupportedAnalyticsModules(self, ConfigurationToken):
        return self.operator.call(
            "GetSupportedAnalyticsModules", ConfigurationToken=ConfigurationToken
        )

    def CreateAnalyticsModules(self, ConfigurationToken, AnalyticsModule):
        return self.operator.call(
            "CreateAnalyticsModules",
            ConfigurationToken=ConfigurationToken,
            AnalyticsModule=AnalyticsModule,
        )

    def DeleteAnalyticsModules(self, ConfigurationToken, AnalyticsModuleName):
        return self.operator.call(
            "DeleteAnalyticsModules",
            ConfigurationToken=ConfigurationToken,
            AnalyticsModuleName=AnalyticsModuleName,
        )

    def GetAnalyticsModules(self, ConfigurationToken):
        return self.operator.call(
            "GetAnalyticsModules", ConfigurationToken=ConfigurationToken
        )

    def GetAnalyticsModuleOptions(self, ConfigurationToken, Type=None):
        return self.operator.call(
            "GetAnalyticsModuleOptions",
            Type=Type,
            ConfigurationToken=ConfigurationToken,
        )

    def ModifyAnalyticsModules(self, ConfigurationToken, AnalyticsModule):
        return self.operator.call(
            "ModifyAnalyticsModules",
            ConfigurationToken=ConfigurationToken,
            AnalyticsModule=AnalyticsModule,
        )

    def GetSupportedMetadata(self, Type=None):
        return self.operator.call("GetSupportedMetadata", Type=Type)
