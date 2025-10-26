# onvif/services/doorcontrol.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class DoorControl(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.3 (May 2013) Release Notes
        # - DoorControlBinding (ver10/pacs/doorcontrol.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/pacs/doorcontrol.wsdl

        definition = ONVIFWSDL.get_definition("doorcontrol")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="DoorControl",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetDoorInfoList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetDoorInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetDoorInfo(self, Token):
        return self.operator.call("GetDoorInfo", Token=Token)

    def GetDoorList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetDoorList", Limit=Limit, StartReference=StartReference
        )

    def GetDoors(self, Token):
        return self.operator.call("GetDoors", Token=Token)

    def CreateDoor(self, Door):
        return self.operator.call("CreateDoor", Door=Door)

    def SetDoor(self, Door):
        return self.operator.call("SetDoor", Door=Door)

    def ModifyDoor(self, Door):
        return self.operator.call("ModifyDoor", Door=Door)

    def DeleteDoor(self, Token):
        return self.operator.call("DeleteDoor", Token=Token)

    def GetDoorState(self, Token):
        return self.operator.call("GetDoorState", Token=Token)

    def AccessDoor(
        self,
        Token,
        UseExtendedTime=None,
        AccessTime=None,
        OpenTooLongTime=None,
        PreAlarmTime=None,
        Extension=None,
    ):
        return self.operator.call(
            "AccessDoor",
            Token=Token,
            UseExtendedTime=UseExtendedTime,
            AccessTime=AccessTime,
            OpenTooLongTime=OpenTooLongTime,
            PreAlarmTime=PreAlarmTime,
            Extension=Extension,
        )

    def LockDoor(self, Token):
        return self.operator.call("LockDoor", Token=Token)

    def UnlockDoor(self, Token):
        return self.operator.call("UnlockDoor", Token=Token)

    def BlockDoor(self, Token):
        return self.operator.call("BlockDoor", Token=Token)

    def LockDownDoor(self, Token):
        return self.operator.call("LockDownDoor", Token=Token)

    def LockDownReleaseDoor(self, Token):
        return self.operator.call("LockDownReleaseDoor", Token=Token)

    def LockOpenDoor(self, Token):
        return self.operator.call("LockOpenDoor", Token=Token)

    def LockOpenReleaseDoor(self, Token):
        return self.operator.call("LockOpenReleaseDoor", Token=Token)

    def DoubleLockDoor(self, Token):
        return self.operator.call("DoubleLockDoor", Token=Token)
