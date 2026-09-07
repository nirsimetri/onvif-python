"""Imaging service implementation."""

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Imaging(ONVIFService):
    """Imaging service client.

    References:
        - First introduced: ONVIF Release 2.1 (June 2011) Split from Core 2.0
        - Binding name: `ImagingBinding` (ver20/imaging/wsdl/imaging.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver20/imaging/wsdl/imaging.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Imaging.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("imaging", "ver20")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Imaging",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the imaging service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetImagingSettings(self, VideoSourceToken):
        """Get the ImagingConfiguration for the requested VideoSource."""
        return self.operator.call(
            "GetImagingSettings", VideoSourceToken=VideoSourceToken
        )

    def SetImagingSettings(
        self, VideoSourceToken, ImagingSettings, ForcePersistence=None
    ):
        """Set the ImagingConfiguration for the requested VideoSource."""
        return self.operator.call(
            "SetImagingSettings",
            VideoSourceToken=VideoSourceToken,
            ImagingSettings=ImagingSettings,
            ForcePersistence=ForcePersistence,
        )

    def GetOptions(self, VideoSourceToken):
        """This operation gets the valid ranges for the imaging parameters that have
        device specific ranges.

        This command is mandatory for all device implementing the imaging service. The
        command returns all supported parameters and their ranges such that these can be
        applied to the SetImagingSettings command.

        For read-only parameters which cannot be modified via the SetImagingSettings
        command only a single option or identical Min and Max values is provided.
        """
        return self.operator.call("GetOptions", VideoSourceToken=VideoSourceToken)

    def Move(self, VideoSourceToken, Focus):
        """The Move command moves the focus lens in an absolute, a relative or in a
        continuous manner from its current position.

        The speed argument is optional for absolute and relative control, but required
        for continuous. If no speed argument is used, the default speed is used. Focus
        adjustments through this operation will turn off the autofocus. A device with
        support for remote focus control should support absolute, relative or continuous
        control through the Move operation. The supported MoveOpions are signalled via
        the GetMoveOptions command. At least one focus control capability is required
        for this operation to be functional.

        The move operation contains the following commands:

        Absolute – Requires position parameter and optionally takes a speed argument. A
        unitless type is used by default for focus positioning and speed. Optionally, if
        supported, the position may be requested in m-1 units.

        Relative – Requires distance parameter and optionally takes a speed argument.
        Negative distance means negative direction. Continuous – Requires a speed
        argument. Negative speed argument means negative direction.
        """
        return self.operator.call(
            "Move", VideoSourceToken=VideoSourceToken, Focus=Focus
        )

    def Stop(self, VideoSourceToken):
        """The Stop command stops all ongoing focus movements of the lense.

        A device with support for remote focus control as signalled via the
        GetMoveOptions supports this command.

        The operation will not affect ongoing autofocus operation.
        """
        return self.operator.call("Stop", VideoSourceToken=VideoSourceToken)

    def GetStatus(self, VideoSourceToken):
        """Via this command the current status of the Move operation can be requested.

        Supported for this command is available if the support for the Move operation is
        signalled via GetMoveOptions.
        """
        return self.operator.call("GetStatus", VideoSourceToken=VideoSourceToken)

    def GetMoveOptions(self, VideoSourceToken):
        """Imaging move operation options supported for the Video source."""
        return self.operator.call("GetMoveOptions", VideoSourceToken=VideoSourceToken)

    def GetPresets(self, VideoSourceToken):
        """Via this command the list of available Imaging Presets can be requested."""
        return self.operator.call("GetPresets", VideoSourceToken=VideoSourceToken)

    def GetCurrentPreset(self, VideoSourceToken):
        """Via this command the last Imaging Preset applied can be requested.

        If the camera configuration does not match any of the existing Imaging Presets,
        the output of GetCurrentPreset shall be Empty. GetCurrentPreset shall return 0
        if Imaging Presets are not supported by the Video Source.
        """
        return self.operator.call("GetCurrentPreset", VideoSourceToken=VideoSourceToken)

    def SetCurrentPreset(self, VideoSourceToken, PresetToken):
        """The SetCurrentPreset command shall request a given Imaging Preset to be
        applied to the specified Video Source.

        SetCurrentPreset shall only be available for Video Sources with Imaging Presets
        Capability. Imaging Presets are defined by the Manufacturer, and offered as a
        tool to simplify Imaging Settings adjustments for specific scene content. When
        the new Imaging Preset is applied by SetCurrentPreset, the Device shall adjust
        the Video Source settings to match those defined by the specified Imaging
        Preset.
        """
        return self.operator.call(
            "SetCurrentPreset",
            VideoSourceToken=VideoSourceToken,
            PresetToken=PresetToken,
        )
