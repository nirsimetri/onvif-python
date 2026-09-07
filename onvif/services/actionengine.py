"""ActionEngine service implementation."""

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class ActionEngine(ONVIFService):
    """ActionEngine service client.

    References:
        - First introduced: ONVIF Release 2.2 (September 2012)
        - Binding name: `ActionEngineBinding` (ver10/actionengine.wsdl).
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/actionengine.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/ActionEngine.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("actionengine")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="ActionEngine",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """The get capabilities operation returns the Action Engine capabilities."""
        return self.operator.call("GetServiceCapabilities")

    def GetSupportedActions(self):
        """The service provider returns the supported action types.

        The response returns a list of Action Descriptions according to the Action
        Description Language.

        The response also contains a list of URLs that provide the location of the
        schema files. These schema files describe the types and elements used in the
        Action Descriptions. If action descriptions reference types or elements of the
        ONVIF schema file, the ONVIF schema file shall be explicitly listed.
        """
        return self.operator.call("GetSupportedActions")

    def GetActions(self):
        """The service provider returns currently installed Actions."""
        return self.operator.call("GetActions")

    def CreateActions(self, Action):
        """The create action operation adds actions to configuration.

        The create action operation is atomic. If a service provider can not create all
        of requested actions, the service provider responds with a fault message.
        """
        return self.operator.call("CreateActions", Action=Action)

    def DeleteActions(self, Token):
        """The delete operation deletes actions.

        The delete action operation is atomic. If a service provider can not delete all
        of requested actions, the service provider responds with a fault message.
        """
        return self.operator.call("DeleteActions", Token=Token)

    def ModifyActions(self, Action):
        """The modify action operation modifies action configurations.

        The modify action operation is atomic. If a service provider can not modify all
        of requested action configurations, the service provider responds with a fault
        message.

        All action parameters, except the action type, can be modified. The service
        provider shall return InvalidAction error if the request attempts to change the
        action type with modify action request.
        """
        return self.operator.call("ModifyActions", Action=Action)

    def GetActionTriggers(self):
        """The service provider returns existing action triggers."""
        return self.operator.call("GetActionTriggers")

    def CreateActionTriggers(self, ActionTrigger):
        """Creates action triggers.

        The create action triggers operation is atomic. If a service provider can not
        create all of requested action triggers, the service provider responds with a
        fault message.
        """
        return self.operator.call("CreateActionTriggers", ActionTrigger=ActionTrigger)

    def DeleteActionTriggers(self, Token):
        """Deletes action triggers.

        The delete action triggers operation is atomic. If a service provider can not
        delete all of requested action triggers, the service provider responds with a
        fault message.
        """
        return self.operator.call("DeleteActionTriggers", Token=Token)

    def ModifyActionTriggers(self, ActionTrigger):
        """Modifies existing action triggers.

        The modify action triggers operation is atomic. If a service provider can not
        modify all of requested action trigger configurations, the service provider
        responds with a fault message.
        """
        return self.operator.call("ModifyActionTriggers", ActionTrigger=ActionTrigger)
