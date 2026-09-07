"""WS-BaseNotification subscription management implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Subscription(ONVIFService):
    """WS-BaseNotification SubscriptionManager service client.

    This interface manages the lifecycle of a notification subscription created
    through the WS-BaseNotification NotificationProducer interface.

    SubscriptionManager endpoints are typically returned as SubscriptionReference
    values when creating an event or pull point subscription.

    References:
        - ONVIF Core Specification
        - OASIS WS-BaseNotification Specification
        - Binding name: `SubscriptionManagerBinding` (ver10/events/wsdl/event-vs.wsdl)
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("subscription")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def Renew(self, TerminationTime=None):
        """An ONVIF compliant device shall support this command if it signals support
        for [WS-Base Notification] via the MaxNotificationProducers capability.

        The command shall at least support a Timeout of one minute. A device shall
        respond with both parameters CurrentTime and TerminationTime as utc using the
        'Z' indicator.
        """
        return self.operator.call("Renew", TerminationTime=TerminationTime)

    def Unsubscribe(self):
        """The device shall provide the following Unsubscribe command for all
        SubscriptionManager endpoints returned by the CreatePullPointSubscription
        command.

        The command is defined in section 6.1.2 of [OASIS Web Services Base Notification
        1.3].

        This command shall terminate the lifetime of a pull point.
        """
        return self.operator.call("Unsubscribe")
