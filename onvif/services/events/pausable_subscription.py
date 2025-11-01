# onvif/services/events/pausable_subscription.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class PausableSubscription(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - PausableSubscriptionManagerBinding (ver10/events/wsdl/event-vs.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/events/wsdl/event.wsdl

        definition = ONVIFWSDL.get_definition("pausable_subscription")
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

    def PauseSubscription(self):
        return self.operator.call("PauseSubscription")

    def ResumeSubscription(self):
        return self.operator.call("ResumeSubscription")
