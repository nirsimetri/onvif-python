# onvif/services/events/subscription.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL


class Subscription:
    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("subscription")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def Renew(self, TerminationTime=None):
        return self.operator.call("Renew", TerminationTime=TerminationTime)

    def Unsubscribe(self):
        return self.operator.call("Unsubscribe")
