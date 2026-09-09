"""Events (Core) service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Events(ONVIFService):
    """Events service client.

    References:
    - ONVIF Core
    - Binding name: `EventBinding` (ver10/events/wsdl/event-vs.wsdl)
    - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/events/wsdl/event.wsdl
    - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Core.xml
    """

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
        """Returns the capabilities of the event service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def CreatePullPointSubscription(
        self, Filter=None, InitialTerminationTime=None, SubscriptionPolicy=None
    ):
        """This method returns a PullPointSubscription that can be polled using
        PullMessages.

        This message contains the same elements as the SubscriptionRequest of the WS-
        BaseNotification without the ConsumerReference.

        If no Filter is specified the pullpoint notifies all occurring events to the
        client.

        This method is mandatory.
        """
        return self.operator.call(
            "CreatePullPointSubscription",
            Filter=Filter,
            InitialTerminationTime=InitialTerminationTime,
            SubscriptionPolicy=SubscriptionPolicy,
        )

    def GetEventProperties(self):
        """The WS-BaseNotification specification defines a set of OPTIONAL WS-
        ResouceProperties.

        This specification does not require the implementation of the WS-
        ResourceProperty interface. Instead, the subsequent direct interface shall be
        implemented by an ONVIF compliant device in order to provide information about
        the FilterDialects, Schema files and topics supported by the device.
        """
        return self.operator.call("GetEventProperties")

    def AddEventBroker(self, EventBroker):
        """The AddEventBroker command allows an ONVIF client to add an event broker
        configuration to device to enable ONVIF events to be transferred to an event
        broker.

        If an existing event broker configuration already exists with the same Address,
        the existing configuration shall be modified.
        """
        return self.operator.call("AddEventBroker", EventBroker=EventBroker)

    def DeleteEventBroker(self, Address):
        """The DeleteEventBroker allows an ONVIF client to delete an event broker
        configuration from an ONVIF device."""
        return self.operator.call("DeleteEventBroker", Address=Address)

    def GetEventBrokers(self, Address=None):
        """The GetEventBrokers command lets a client retrieve event broker
        configurations from the device."""
        return self.operator.call("GetEventBrokers", Address=Address)
