# onvif/services/replay.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL


class Replay:
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
        return self.operator.call("GetServiceCapabilities")

    def GetReplayUri(self, StreamSetup, RecordingToken):
        return self.operator.call(
            "GetReplayUri", StreamSetup=StreamSetup, RecordingToken=RecordingToken
        )

    def GetReplayConfiguration(self):
        return self.operator.call("GetReplayConfiguration")

    def SetReplayConfiguration(self, Configuration):
        return self.operator.call("SetReplayConfiguration", Configuration=Configuration)
