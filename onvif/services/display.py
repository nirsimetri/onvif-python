"""Display service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Display(ONVIFService):
    """Display service client.

    References:
        - First introduced: ONVIF Release 2.1 (June 2011) Split from Core 2.0
        - Binding name: `DisplayBinding` (ver10/display.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/display.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Display.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("display")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Display",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the display service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetLayout(self, VideoOutput):
        """Return the current layout of a video output.

        The Layout assigns a pane configuration to a certain area of the display. The
        layout settings directly affect a specific video output. The layout consists of
        a list of PaneConfigurations and their associated display areas.
        """
        return self.operator.call("GetLayout", VideoOutput=VideoOutput)

    def SetLayout(self, VideoOutput, Layout):
        """Change the layout of a display (e.g. change from single view to split screen
        view).The Layout assigns a pane configuration to a certain area of the display.

        The layout settings directly affect a specific video output. The layout consists
        of a list of PaneConfigurations and their associated display areas.

        A device implementation shall be tolerant against rounding errors when matching
        a layout against its fixed set of layouts by accepting differences of at least
        one percent.
        """
        return self.operator.call("SetLayout", VideoOutput=VideoOutput, Layout=Layout)

    def GetDisplayOptions(self, VideoOutput):
        """The Display Options contain the supported layouts (LayoutOptions) and the
        decoding and encoding capabilities (CodingCapabilities) of the device.

        The GetDisplayOptions command returns both, Layout and Coding Capabilities, of a
        VideoOutput.
        """
        return self.operator.call("GetDisplayOptions", VideoOutput=VideoOutput)

    def GetPaneConfigurations(self, VideoOutput):
        """List all currently defined panes of a device for a specified video output
        (regardless if this pane is visible at a moment).

        A Pane is a display area on the monitor that is attached to a video output. A
        pane has a PaneConfiguration that describes which entities are associated with
        the pane. A client has to configure the pane according to the connection to be
        established by setting the AudioOutput and/or AudioSourceToken. If a Token is
        not set, the corresponding session will not be established.
        """
        return self.operator.call("GetPaneConfigurations", VideoOutput=VideoOutput)

    def GetPaneConfiguration(self, VideoOutput, Pane):
        """Retrieve the pane configuration for a pane token."""
        return self.operator.call(
            "GetPaneConfiguration", VideoOutput=VideoOutput, Pane=Pane
        )

    def SetPaneConfigurations(self, VideoOutput, PaneConfiguration):
        """Modify one or more configurations of the specified video output.

        This method will only modify the provided configurations and leave the others
        unchanged. Use DeletePaneConfiguration to remove pane configurations.
        """
        return self.operator.call(
            "SetPaneConfigurations",
            VideoOutput=VideoOutput,
            PaneConfiguration=PaneConfiguration,
        )

    def SetPaneConfiguration(self, VideoOutput, PaneConfiguration):
        """This command changes the configuration of the specified pane (tbd)"""
        return self.operator.call(
            "SetPaneConfiguration",
            VideoOutput=VideoOutput,
            PaneConfiguration=PaneConfiguration,
        )

    def CreatePaneConfiguration(self, VideoOutput, PaneConfiguration):
        """Create a new pane configuration describing the streaming and coding settings
        for a display area.

        This optional method is only supported by devices that signal support of dynamic
        pane creation via their capabilities.

        The content of the Token field may be ignored by the device.
        """
        return self.operator.call(
            "CreatePaneConfiguration",
            VideoOutput=VideoOutput,
            PaneConfiguration=PaneConfiguration,
        )

    def DeletePaneConfiguration(self, VideoOutput, PaneToken):
        """Delete a pane configuration.

        A service must respond with an error if the pane configuration is in use by the
        current layout.

        This optional method is only supported by devices that signal support of dynamic
        pane creation via their capabilities.
        """
        return self.operator.call(
            "DeletePaneConfiguration", VideoOutput=VideoOutput, PaneToken=PaneToken
        )
