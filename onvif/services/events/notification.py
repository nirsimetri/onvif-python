# onvif/services/events/notification.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class Notification(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - NotificationProducerBinding (ver10/events/wsdl/event-vs.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/events/wsdl/event.wsdl

        definition = ONVIFWSDL.get_definition("notification")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Events",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def Subscribe(
        self,
        ConsumerReference=None,
        Filter=None,
        InitialTerminationTime=None,
        SubscriptionPolicy=None,
    ):
        return self.operator.call(
            "Subscribe",
            ConsumerReference=ConsumerReference,
            Filter=Filter,
            InitialTerminationTime=InitialTerminationTime,
            SubscriptionPolicy=SubscriptionPolicy,
        )

    def GetCurrentMessage(self, Topic):
        return self.operator.call("GetCurrentMessage", Topic=Topic)
