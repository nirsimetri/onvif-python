# onvif/services/accessrules.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL


class AccessRules:
    def __init__(self, xaddr=None, **kwargs):
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
