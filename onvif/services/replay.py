# onvif/services/replay.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Replay(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.1 (June 2011) Split from Core 2.0
        # - ReplayBinding (ver10/replay.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/replay.wsdl

        definition = ONVIFWSDL.get_definition("replay")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Replay",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetReplayUri(self, StreamSetup, RecordingToken):
        return self.operator.call(
            "GetReplayUri", StreamSetup=StreamSetup, RecordingToken=RecordingToken
        )

    def GetReplayConfiguration(self):
        return self.operator.call("GetReplayConfiguration")

    def SetReplayConfiguration(self, Configuration):
        return self.operator.call("SetReplayConfiguration", Configuration=Configuration)
