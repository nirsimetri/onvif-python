# onvif/services/receiver.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Receiver(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.1 (June 2011) Split from Core 2.0
        # - ReceiverBinding (ver10/receiver.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/receiver.wsdl

        definition = ONVIFWSDL.get_definition("receiver")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Receiver",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetReceivers(self):
        return self.operator.call("GetReceivers")

    def GetReceiver(self, ReceiverToken):
        return self.operator.call("GetReceiver", ReceiverToken=ReceiverToken)

    def CreateReceiver(self, Configuration):
        return self.operator.call("CreateReceiver", Configuration=Configuration)

    def DeleteReceiver(self, ReceiverToken):
        return self.operator.call("DeleteReceiver", ReceiverToken=ReceiverToken)

    def ConfigureReceiver(self, ReceiverToken, Configuration):
        return self.operator.call(
            "ConfigureReceiver",
            ReceiverToken=ReceiverToken,
            Configuration=Configuration,
        )

    def SetReceiverMode(self, ReceiverToken, Mode):
        return self.operator.call(
            "SetReceiverMode", ReceiverToken=ReceiverToken, Mode=Mode
        )

    def GetReceiverState(self, ReceiverToken):
        return self.operator.call("GetReceiverState", ReceiverToken=ReceiverToken)
