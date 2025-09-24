# onvif/services/events/events.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL


class Events:
    def __init__(self, xaddr=None, **kwargs):
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
