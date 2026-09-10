"""Thermal service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Thermal(ONVIFService):
    """Thermal service client.

    | Property | Details |
    | --- | --- |
    | **First introduced** | ONVIF Release 16.06 (June 2016) |
    | **Binding name** | `ThermalBinding` (`ver10/thermal/wsdl/thermal.wsdl`) |
    | **Operations** | [thermal.wsdl)]([thermal.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/thermal/wsdl/thermal.wsdl)) |
    | **Specification** | [Thermal.xml)]([Thermal.xml](https://developer.onvif.org/pub/specs/branches/development/doc/Thermal.xml)) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("thermal")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Thermal",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the thermal service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetConfigurationOptions(self, VideoSourceToken):
        """Gets the valid ranges for the Thermal parameters that have device specific
        ranges.

        This command is mandatory for all devices implementing the Thermal service. The
        command shall return all supported parameters and their ranges, such that these
        can be applied to the SetConfiguration command.
        """
        return self.operator.call(
            "GetConfigurationOptions", VideoSourceToken=VideoSourceToken
        )

    def GetConfiguration(self, VideoSourceToken):
        """Gets the Thermal Configuration for the requested VideoSource."""
        return self.operator.call("GetConfiguration", VideoSourceToken=VideoSourceToken)

    def GetConfigurations(self):
        """Gets the Thermal Configuration for all thermal VideoSources of the Device."""
        return self.operator.call("GetConfigurations")

    def SetConfiguration(self, VideoSourceToken, Configuration):
        """Sets the Thermal Configuration for the requested VideoSource."""
        return self.operator.call(
            "SetConfiguration",
            VideoSourceToken=VideoSourceToken,
            Configuration=Configuration,
        )

    def GetRadiometryConfigurationOptions(self, VideoSourceToken):
        """Gets the valid ranges for the Radiometry parameters that have device specific
        ranges.

        The command shall return all supported parameters and their ranges, such that
        these can be applied to the SetRadiometryConfiguration command.
        """
        return self.operator.call(
            "GetRadiometryConfigurationOptions", VideoSourceToken=VideoSourceToken
        )

    def GetRadiometryConfiguration(self, VideoSourceToken):
        """Gets the Radiometry Configuration for the requested VideoSource."""
        return self.operator.call(
            "GetRadiometryConfiguration", VideoSourceToken=VideoSourceToken
        )

    def SetRadiometryConfiguration(self, VideoSourceToken, Configuration):
        """Sets the Radiometry Configuration for the requested VideoSource."""
        return self.operator.call(
            "SetRadiometryConfiguration",
            VideoSourceToken=VideoSourceToken,
            Configuration=Configuration,
        )
