"""Events (PullPoint) service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class PullPoint(ONVIFService):
    """Events (PullPoint) service client.

    References:
    - ONVIF Core
    - Binding name: `PullPointSubscriptionBinding` (ver10/events/wsdl/event-vs.wsdl)
    - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/events/wsdl/event.wsdl
    - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/Core.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("pullpoint")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def PullMessages(self, Timeout, MessageLimit):
        """This method pulls one or more messages from a PullPoint.

        The device shall provide the following PullMessages command for all
        SubscriptionManager endpoints returned by the CreatePullPointSubscription
        command. This method shall not wait until the requested number of messages is
        available but return as soon as at least one message is available.

        The command shall at least support a Timeout of one minute. In case a device
        supports retrieval of less messages than requested it shall return these without
        generating a fault.
        """
        return self.operator.call(
            "PullMessages", Timeout=Timeout, MessageLimit=MessageLimit
        )

    def Seek(self, UtcTime, Reverse=None):
        """This method readjusts the pull pointer into the past.

        A device supporting persistent notification storage shall provide the following
        Seek command for all SubscriptionManager endpoints returned by the
        CreatePullPointSubscription command. The optional Reverse argument can be used
        to reverse the pull direction of the PullMessages command.

        The UtcTime argument will be matched against the UtcTime attribute on a
        NotificationMessage.
        """
        return self.operator.call("Seek", UtcTime=UtcTime, Reverse=Reverse)

    def SetSynchronizationPoint(self):
        """Properties inform a client about property creation, changes and deletion in a
        uniform way.

        When a client wants to synchronize its properties with the properties of the
        device, it can request a synchronization point which repeats the current status
        of all properties to which a client has subscribed. The PropertyOperation of all
        produced notifications is set to "Initialized". The Synchronization Point is
        requested directly from the SubscriptionManager which was returned in either the
        SubscriptionResponse or in the CreatePullPointSubscriptionResponse. The property
        update is transmitted via the notification transportation of the notification
        interface. This method is mandatory.
        """
        return self.operator.call("SetSynchronizationPoint")

    def Unsubscribe(self):
        """The device shall provide the following Unsubscribe command for all
        SubscriptionManager endpoints returned by the CreatePullPointSubscription
        command.

        This command shall terminate the lifetime of a pull point.
        """
        return self.operator.call("Unsubscribe")
