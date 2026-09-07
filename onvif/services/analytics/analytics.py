"""Analytics service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Analytics(ONVIFService):
    """Analytics service client.

    References:
        - First introduced: ONVIF Release 2.41 (December 2013)
        - Binding name: `AnalyticsEngineBinding` (ver20/analytics/wsdl/analytics.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/analytics/wsdl/analytics.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Analytics.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("analytics", "ver20")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Analytics",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the analytics service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetSupportedAnalyticsModules(self, ConfigurationToken):
        """List all analytics modules that are supported by the given
        VideoAnalyticsConfiguration."""
        return self.operator.call(
            "GetSupportedAnalyticsModules", ConfigurationToken=ConfigurationToken
        )

    def CreateAnalyticsModules(self, ConfigurationToken, AnalyticsModule):
        """Add one or more analytics modules to an existing VideoAnalyticsConfiguration.

        The available supported types can be retrieved via GetSupportedAnalyticsModules,
        where the Name of the supported AnalyticsModules correspond to the type of an
        AnalyticsModule instance.

        Pass unique module names which can be later used as reference. The Parameters of
        the analytics module must match those of the corresponding
        AnalyticsModuleDescription.

        Although this method is mandatory a device implementation may not support adding
        modules. Instead it can provide a fixed set of predefined configurations via the
        media service functions GetCompatibleVideoAnalyticsConfigurations and
        GetAnalyticsConfigurations.

        The device shall ensure that a corresponding analytics engine starts operation
        when a client subscribes directly or indirectly for events produced by the
        analytics or rule engine or when a client requests the corresponding scene
        description stream. An analytics module must be attached to a Video source using
        the media profiles before it can be used. In case differing analytics
        configurations are attached to the same profile it is undefined which of the
        analytics module configuration becomes active if no stream is activated or
        multiple streams with different profiles are activated at the same time.
        """
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
