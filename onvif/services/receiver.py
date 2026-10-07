"""Receiver service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils.service import ONVIFService
from onvif.utils.wsdl import ONVIFWSDL


class Receiver(ONVIFService):
    """Receiver service client.

    | Property | Details |
    | -------- | ------- |
    | **First introduced** | ONVIF Release 2.1 (June 2011) split from Core 2.0 |
    | **Binding name** | `ReceiverBinding` (`ver10/receiver.wsdl`) |
    | **Operations** | [receiver.wsdl](https://www.onvif.org/ver10/receiver.wsdl) |
    | **Spec** | [Receiver](https://www.onvif.org/specs/srv/rcv/ONVIF-Receiver-Service-Spec.pdf) |
    | **Data Format** | [Streaming](https://www.onvif.org/specs/stream/ONVIF-Streaming-Spec.pdf) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("receiver")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Receiver",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """Returns the capabilities of the receiver service.

        The result is returned in a typed answer.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetReceivers(self):
        """Lists all receivers currently present on a device.

        This operation is mandatory.
        """
        return self.operator.call("GetReceivers")

    def GetReceiver(self, ReceiverToken):
        """Retrieves the details of a specific receiver.

        This operation is mandatory.
        """
        return self.operator.call("GetReceiver", ReceiverToken=ReceiverToken)

    def CreateReceiver(self, Configuration):
        """Creates a new receiver.

        This operation is mandatory, although the service may raise a fault if the
        receiver cannot be created.
        """
        return self.operator.call("CreateReceiver", Configuration=Configuration)

    def DeleteReceiver(self, ReceiverToken):
        """Deletes an existing receiver.

        A receiver may be deleted only if it is not currently in use; otherwise a fault
        shall be raised. This operation is mandatory.
        """
        return self.operator.call("DeleteReceiver", ReceiverToken=ReceiverToken)

    def ConfigureReceiver(self, ReceiverToken, Configuration):
        """Configures an existing receiver.

        This operation is mandatory.
        """
        return self.operator.call(
            "ConfigureReceiver",
            ReceiverToken=ReceiverToken,
            Configuration=Configuration,
        )

    def SetReceiverMode(self, ReceiverToken, Mode):
        """Sets the mode of the receiver without affecting the rest of its
        configuration.

        This operation is mandatory.
        """
        return self.operator.call(
            "SetReceiverMode", ReceiverToken=ReceiverToken, Mode=Mode
        )

    def GetReceiverState(self, ReceiverToken):
        """Determines whether the receiver is currently disconnected, connected or
        attempting to connect.

        This operation is mandatory.
        """
        return self.operator.call("GetReceiverState", ReceiverToken=ReceiverToken)
