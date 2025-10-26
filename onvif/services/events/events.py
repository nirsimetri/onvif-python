# onvif/services/events/events.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


class Events(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Core
        # - EventBinding (ver10/events/wsdl/event-vs.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/events/wsdl/event.wsdl

        definition = ONVIFWSDL.get_definition("events")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Events",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def CreatePullPointSubscription(
        self, Filter=None, InitialTerminationTime=None, SubscriptionPolicy=None
    ):
        return self.operator.call(
            "CreatePullPointSubscription",
            Filter=Filter,
            InitialTerminationTime=InitialTerminationTime,
            SubscriptionPolicy=SubscriptionPolicy,
        )

    def GetEventProperties(self):
        return self.operator.call("GetEventProperties")

    def AddEventBroker(self, EventBroker):
        return self.operator.call("AddEventBroker", EventBroker=EventBroker)

    def DeleteEventBroker(self, Address):
        return self.operator.call("DeleteEventBroker", Address=Address)

    def GetEventBrokers(self, Address=None):
        return self.operator.call("GetEventBrokers", Address=Address)
