"""Replay service implementation."""

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Replay(ONVIFService):
    """Recording service client.

    References:
    - First introduced: ONVIF Release 2.1 (June 2011) Split from Core 2.0
    - Binding name: `ReplayBinding` (ver10/replay.wsdl)
    - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/replay.wsdl
    - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Replay.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("replay")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Replay",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the replay service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetReplayUri(self, StreamSetup, RecordingToken):
        """Requests a URI that can be used to initiate playback of a recorded stream
        using RTSP as the control protocol.

        The URI is valid only as it is specified in the response. A device supporting
        the Replay Service shall support the GetReplayUri command.
        """
        return self.operator.call(
            "GetReplayUri", StreamSetup=StreamSetup, RecordingToken=RecordingToken
        )

    def GetReplayConfiguration(self):
        """Returns the current configuration of the replay service.

        This operation is mandatory.
        """
        return self.operator.call("GetReplayConfiguration")

    def SetReplayConfiguration(self, Configuration):
        """Changes the current configuration of the replay service.

        This operation is mandatory.
        """
        return self.operator.call("SetReplayConfiguration", Configuration=Configuration)
