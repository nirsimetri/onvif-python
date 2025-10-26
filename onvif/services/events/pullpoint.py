# onvif/services/events/pullpoint.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class PullPoint(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - PullPointSubscriptionBinding (ver10/events/wsdl/event-vs.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/events/wsdl/event.wsdl

        definition = ONVIFWSDL.get_definition("pullpoint")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def PullMessages(self, Timeout, MessageLimit):
        return self.operator.call(
            "PullMessages", Timeout=Timeout, MessageLimit=MessageLimit
        )

    def Seek(self, UtcTime, Reverse=None):
        return self.operator.call("Seek", UtcTime=UtcTime, Reverse=Reverse)

    def SetSynchronizationPoint(self):
        return self.operator.call("SetSynchronizationPoint")

    def Unsubscribe(self):
        return self.operator.call("Unsubscribe")
