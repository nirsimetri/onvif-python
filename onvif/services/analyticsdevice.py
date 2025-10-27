# onvif/services/analyticsdevice.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class AnalyticsDevice(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # NOTE (ONVIF 18.12):
        # The AnalyticsDevice service (AnalyticsDeviceBinding) has been marked as
        # obsolete since ONVIF Release 18.12. Its functionality has largely been
        # merged into the Analytics service and, in some cases, Media2.
        #
        # This class is kept here only for backward compatibility with older devices
        # (pre-2019) that may still expose an AnalyticsDevice XAddr.
        #
        # In modern ONVIF-compliant devices, you should prefer using the Analytics
        # service (`onvif/services/analytics/analytics.py`). If the device does not list
        # AnalyticsDevice in `GetServices` response, then this service is not available
        # on the device and calling this class will result in SOAP faults.
        #
        # References:
        # - Introduce in ONVIF Release 2.1 (June 2011) Split from Core 2.0
        # - ONVIF Release 18.12 (December 2018) Release Notes
        # - AnalyticsDeviceBinding (ver10/analyticsdevice.wsdl)
        # - Successor: Analytics Service (ver20/analytics/wsdl/analytics.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/analyticsdevice.wsdl

        definition = ONVIFWSDL.get_definition("analyticsdevice")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="AnalyticsDevice",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def DeleteAnalyticsEngineControl(self, ConfigurationToken):
        return self.operator.call(
            "DeleteAnalyticsEngineControl", ConfigurationToken=ConfigurationToken
        )

    def CreateAnalyticsEngineControl(self, Configuration):
        return self.operator.call(
            "CreateAnalyticsEngineControl", Configuration=Configuration
        )

    def SetAnalyticsEngineControl(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetAnalyticsEngineControl",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def GetAnalyticsEngineControl(self, ConfigurationToken):
        return self.operator.call(
            "GetAnalyticsEngineControl", ConfigurationToken=ConfigurationToken
        )

    def GetAnalyticsEngineControls(self):
        return self.operator.call("GetAnalyticsEngineControls")

    def GetAnalyticsEngine(self, ConfigurationToken):
        return self.operator.call(
            "GetAnalyticsEngine", ConfigurationToken=ConfigurationToken
        )

    def GetAnalyticsEngines(self):
        return self.operator.call("GetAnalyticsEngines")

    def SetVideoAnalyticsConfiguration(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetVideoAnalyticsConfiguration",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def SetAnalyticsEngineInput(self, Configuration, ForcePersistence):
        return self.operator.call(
            "SetAnalyticsEngineInput",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def GetAnalyticsEngineInput(self, ConfigurationToken):
        return self.operator.call(
            "GetAnalyticsEngineInput", ConfigurationToken=ConfigurationToken
        )

    def GetAnalyticsEngineInputs(self):
        return self.operator.call("GetAnalyticsEngineInputs")

    def GetAnalyticsDeviceStreamUri(self, StreamSetup, AnalyticsEngineControlToken):
        return self.operator.call(
            "GetAnalyticsDeviceStreamUri",
            StreamSetup=StreamSetup,
            AnalyticsEngineControlToken=AnalyticsEngineControlToken,
        )

    def GetVideoAnalyticsConfiguration(self, ConfigurationToken):
        return self.operator.call(
            "GetVideoAnalyticsConfiguration", ConfigurationToken=ConfigurationToken
        )

    def CreateAnalyticsEngineInputs(self, Configuration, ForcePersistence):
        return self.operator.call(
            "CreateAnalyticsEngineInputs",
            Configuration=Configuration,
            ForcePersistence=ForcePersistence,
        )

    def DeleteAnalyticsEngineInputs(self, ConfigurationToken):
        return self.operator.call(
            "DeleteAnalyticsEngineInputs", ConfigurationToken=ConfigurationToken
        )

    def GetAnalyticsState(self, AnalyticsEngineControlToken):
        return self.operator.call(
            "GetAnalyticsState", AnalyticsEngineControlToken=AnalyticsEngineControlToken
        )
