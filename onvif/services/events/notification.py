"""WS-BaseNotification service implementation."""

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class Notification(ONVIFService):
    """WS-BaseNotification NotificationProducer service client.

    This service provides access to the NotificationProducer interface used by
    ONVIF devices for push-based event notification subscriptions.

    References:
        - ONVIF Core
        - OASIS WS-BaseNotification Specification
        - Binding name: `NotificationProducerBinding` (ver10/events/wsdl/event-vs.wsdl)
    """

    def __init__(self, xaddr=None, **kwargs):
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
        """Create a subscription for receiving event notifications.

        Registers a notification consumer with the NotificationProducer. Event notifications
        matching the optional filter are delivered to the consumer endpoint specified
        by ConsumerReference.

        Args:
            ConsumerReference: Reference to the notification consumer endpoint.
            Filter: Optional filter used to select notifications of interest.
            InitialTerminationTime: Requested initial subscription termination time.
            SubscriptionPolicy: Optional policy controlling subscription behavior.

        Returns:
            The subscription response containing the SubscriptionReference and termination time.
        """
        return self.operator.call(
            "Subscribe",
            ConsumerReference=ConsumerReference,
            Filter=Filter,
            InitialTerminationTime=InitialTerminationTime,
            SubscriptionPolicy=SubscriptionPolicy,
        )

    def GetCurrentMessage(self, Topic):
        """Retrieve the current message for a notification topic.

        Requests the current state message associated with the specified topic from the
        NotificationProducer.

        Args:
            Topic: Topic identifying the notification message to retrieve.

        Returns:
            The current notification message for the specified topic.
        """
        return self.operator.call("GetCurrentMessage", Topic=Topic)
