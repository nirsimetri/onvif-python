# onvif/services/accessrules.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class AccessRules(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.6 (June 2015) Release Notes
        # - AccessRulesBinding (ver10/accessrules/wsdl/accessrules.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/accessrules/wsdl/accessrules.wsdl

        definition = ONVIFWSDL.get_definition("accessrules")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="AccessRules",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetAccessProfileInfo(self, Token):
        return self.operator.call("GetAccessProfileInfo", Token=Token)

    def GetAccessProfileInfoList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetAccessProfileInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetAccessProfiles(self, Token):
        return self.operator.call("GetAccessProfiles", Token=Token)

    def GetAccessProfileList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetAccessProfileList", Limit=Limit, StartReference=StartReference
        )

    def CreateAccessProfile(self, AccessProfile):
        return self.operator.call("CreateAccessProfile", AccessProfile=AccessProfile)

    def ModifyAccessProfile(self, AccessProfile):
        return self.operator.call("ModifyAccessProfile", AccessProfile=AccessProfile)

    def SetAccessProfile(self, AccessProfile):
        return self.operator.call("SetAccessProfile", AccessProfile=AccessProfile)

    def DeleteAccessProfile(self, Token):
        return self.operator.call("DeleteAccessProfile", Token=Token)
