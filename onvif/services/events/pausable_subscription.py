"""WS-BaseNotification pausable subscription implementation."""

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class PausableSubscription(ONVIFService):
    """WS-BaseNotification PausableSubscriptionManager service client.

    This interface extends the Base Subscription Manager with operations for
    temporarily pausing and resuming notification delivery.

    Support for the Pausable Subscription Manager Interface is optional for
    ONVIF devices.

    References:
        - ONVIF Core Specification
        - OASIS WS-BaseNotification Specification
        - Binding name: `PausableSubscriptionManagerBinding` (ver10/events/wsdl/event-vs.wsdl)
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("pausable_subscription")
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

    def PauseSubscription(self):
        """Temporarily suspend notification delivery for the subscription.

        Successfully processing this request places the subscription in a paused
        state. Notifications can be resumed by calling ResumeSubscription().

        Note:
            Notifications may continue to be produced while the pause request is
            in transit.
        """
        return self.operator.call("PauseSubscription")

    def ResumeSubscription(self):
        """Resume notification delivery for a paused subscription.

        Successfully processing this request returns the subscription to its active
        state and resumes the production of notifications.
        """
        return self.operator.call("ResumeSubscription")
