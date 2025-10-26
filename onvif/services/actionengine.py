# onvif/services/actionengine.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class ActionEngine(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.2 (September 2012) Release Notes
        # - ActionEngineBinding (ver10/actionengine.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/actionengine.wsdl

        definition = ONVIFWSDL.get_definition("actionengine")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="ActionEngine",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetSupportedActions(self):
        return self.operator.call("GetSupportedActions")

    def GetActions(self):
        return self.operator.call("GetActions")

    def CreateActions(self, Action):
        return self.operator.call("CreateActions", Action=Action)

    def DeleteActions(self, Token):
        return self.operator.call("DeleteActions", Token=Token)

    def ModifyActions(self, Action):
        return self.operator.call("ModifyActions", Action=Action)

    def GetActionTriggers(self):
        return self.operator.call("GetActionTriggers")

    def CreateActionTriggers(self, ActionTrigger):
        return self.operator.call("CreateActionTriggers", ActionTrigger=ActionTrigger)

    def DeleteActionTriggers(self, Token):
        return self.operator.call("DeleteActionTriggers", Token=Token)

    def ModifyActionTriggers(self, ActionTrigger):
        return self.operator.call("ModifyActionTriggers", ActionTrigger=ActionTrigger)
