"""AnalyticsDevice service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class AnalyticsDevice(ONVIFService):
    """The AnalyticsDevice service (AnalyticsDeviceBinding) aka 'Video Analytics Device'
    has been marked as obsolete since ONVIF Release 18.12.

    Its functionality has largely been merged into the Analytics service and, in some cases
    Media/Media2.

    This class is kept here only for backward compatibility with older devices (pre-2019) that may
    still expose an AnalyticsDevice XAddr.

    In modern ONVIF-compliant devices, you should prefer using the Analytics or Media/Media2 services.
    If the device does not list AnalyticsDevice in `GetServices` response, then this service is not
    available on the device and calling this class will result in SOAP faults.

    | Property | Details |
    | --- | --- |
    | **First introduced** | ONVIF Release 2.1 (June 2011), split from Core 2.0 |
    | **Deprecated** | ONVIF Release 18.12 (December 2018) |
    | **Binding name** | `AnalyticsDeviceBinding` (`ver10/analyticsdevice.wsdl`) |
    | **Successor** | `Analytics` Service (`ver20/analytics/wsdl/analytics.wsdl`) |
    | **Operations** | [analyticsdevice.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/analyticsdevice.wsdl) |
    | **Specification** | [Video Analytics Device Spec](https://www.onvif.org/specs/srv/analytics/ONVIF-VideoAnalyticsDevice-Service-Spec-v211.pdf) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("analyticsdevice")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="AnalyticsDevice",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the analytics device service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def DeleteAnalyticsEngineControl(self, ConfigurationToken):
        """DeleteAnalyticsEngineControl shall delete a control object ."""
        return self.operator.call(
            "DeleteAnalyticsEngineControl", ConfigurationToken=ConfigurationToken
        )

    def CreateAnalyticsEngineControl(self, Configuration):
        """CreateAnalyticsEngineControl shall create a new control object."""
        return self.operator.call(
            "CreateAnalyticsEngineControl", Configuration=Configuration
        )

    def SetAnalyticsEngineControl(self, Configuration, ForcePersistence):
        """This command modifies the AnalyticsEngineControl configuration."""
        return self.operator.call(
            "SetAnalyticsEngineControl",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def GetAnalyticsEngineControl(self, ConfigurationToken):
        """The GetAnalyticsEngineControl command fetches the analytics engine control if
        the analytics engine control token is known."""
        return self.operator.call(
            "GetAnalyticsEngineControl", ConfigurationToken=ConfigurationToken
        )

    def GetAnalyticsEngineControls(self):
        """This operation lists all available analytics engine controls for the
        device."""
        return self.operator.call("GetAnalyticsEngineControls")

    def GetAnalyticsEngine(self, ConfigurationToken):
        """The GetAnalyticsEngine command fetches the analytics engine configuration if
        the token is known."""
        return self.operator.call(
            "GetAnalyticsEngine", ConfigurationToken=ConfigurationToken
        )

    def GetAnalyticsEngines(self):
        """This operation lists all available analytics engine configurations for the
        device."""
        return self.operator.call("GetAnalyticsEngines")

    def SetVideoAnalyticsConfiguration(self, Configuration, ForcePersistence):
        """A video analytics configuration is modified using this command."""
        return self.operator.call(
            "SetVideoAnalyticsConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAnalyticsEngineInput(self, Configuration, ForcePersistence):
        """This command modifies the analytics engine input configuration."""
        return self.operator.call(
            "SetAnalyticsEngineInput",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def GetAnalyticsEngineInput(self, ConfigurationToken):
        """The GetAnalyticsEngineInput command fetches the input configuration if the
        analytics engine input configuration token is known."""
        return self.operator.call(
            "GetAnalyticsEngineInput", ConfigurationToken=ConfigurationToken
        )

    def GetAnalyticsEngineInputs(self):
        """This operation lists all available analytics engine input configurations for
        the device."""
        return self.operator.call("GetAnalyticsEngineInputs")

    def GetAnalyticsDeviceStreamUri(self, StreamSetup, AnalyticsEngineControlToken):
        """This operation requests a URI that can be used to initiate a live stream
        using RTSP as the control protocol if the token of the AnalyticsEngineControl is
        known."""
        return self.operator.call(
            "GetAnalyticsDeviceStreamUri",
            StreamSetup=StreamSetup,
            AnalyticsEngineControlToken=AnalyticsEngineControlToken,
        )

    def GetVideoAnalyticsConfiguration(self, ConfigurationToken):
        """The GetVideoAnalyticsConfiguration command fetches the video analytics
        configuration if the video analytics configuration token is known."""
        return self.operator.call(
            "GetVideoAnalyticsConfiguration", ConfigurationToken=ConfigurationToken
        )

    def CreateAnalyticsEngineInputs(self, Configuration, ForcePersistence):
        """This command generates one or more analytics engine input configurations."""
        return self.operator.call(
            "CreateAnalyticsEngineInputs",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def DeleteAnalyticsEngineInputs(self, ConfigurationToken):
        """This command deletes analytics engine input configurations if the tokens are
        known."""
        return self.operator.call(
            "DeleteAnalyticsEngineInputs", ConfigurationToken=ConfigurationToken
        )

    def GetAnalyticsState(self, AnalyticsEngineControlToken):
        """GetAnalyticsState returns status information of the referenced
        AnalyticsEngineControl object."""
        return self.operator.call(
            "GetAnalyticsState", AnalyticsEngineControlToken=AnalyticsEngineControlToken
        )
