"""Provisioning service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Provisioning(ONVIFService):
    """Provisioning service client.

    References:
        - First introduced: ONVIF Release 16.12 (December 2016)
        - Binding name: `ProvisioningBinding` (ver10/provisioning/wsdl/provisioning.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/provisioning/wsdl/provisioning.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Provisioning.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("provisioning")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Provisioning",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the provisioning service."""
        return self.operator.call("GetServiceCapabilities")

    def PanMove(self, VideoSource, Direction, Timeout=None):
        """Moves device on the pan axis."""
        return self.operator.call(
            "PanMove", VideoSource=VideoSource, Direction=Direction, Timeout=Timeout
        )

    def TiltMove(self, VideoSource, Direction, Timeout=None):
        """Moves device on the tilt axis."""
        return self.operator.call(
            "TiltMove", VideoSource=VideoSource, Direction=Direction, Timeout=Timeout
        )

    def ZoomMove(self, VideoSource, Direction, Timeout=None):
        """Moves device on the zoom axis."""
        return self.operator.call(
            "ZoomMove", VideoSource=VideoSource, Direction=Direction, Timeout=Timeout
        )

    def RollMove(self, VideoSource, Direction, Timeout=None):
        """Moves device on the roll axis."""
        return self.operator.call(
            "RollMove", VideoSource=VideoSource, Direction=Direction, Timeout=Timeout
        )

    def FocusMove(self, VideoSource, Direction, Timeout=None):
        """Moves device on the focus axis."""
        return self.operator.call(
            "FocusMove", VideoSource=VideoSource, Direction=Direction, Timeout=Timeout
        )

    def Stop(self, VideoSource):
        """Stops device motion on all axes."""
        return self.operator.call("Stop", VideoSource=VideoSource)

    def GetUsage(self, VideoSource):
        """Returns the lifetime move counts."""
        return self.operator.call("GetUsage", VideoSource=VideoSource)
