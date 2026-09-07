"""DoorControl service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils import ONVIFWSDL, ONVIFService


# pylint: disable=invalid-name
class DoorControl(ONVIFService):
    """DoorControl service client.

    References:
        - First introduced: ONVIF Release 2.3 (May 2013)
        - Binding name: `DoorControlBinding` (ver10/pacs/doorcontrol.wsdl)
        - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/pacs/doorcontrol.wsdl
        - Specs: https://developer.onvif.org/pub/specs/branches/development/doc/DoorControl.xml
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("doorcontrol")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="DoorControl",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """This operation returns the capabilities of the service.

        An ONVIF compliant device which provides the Door Control service shall
        implement this method.
        """
        return self.operator.call("GetServiceCapabilities")

    def GetDoorInfoList(self, Limit=None, StartReference=None):
        """This operation requests a list of all DoorInfo items provided by the device.

        An ONVIF compliant device that provides Door Control service shall implement
        this method. A call to this method shall return a StartReference when not all
        data is returned and more data is available. The reference shall be valid for
        retrieving the next set of data. The number of items returned shall not be
        greater than Limit parameter.
        """
        return self.operator.call(
            "GetDoorInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetDoorInfo(self, Token):
        """This operation requests a list of DoorInfo items matching the given tokens.

        An ONVIF-compliant device that provides Door Control service shall implement
        this method. The device shall ignore tokens it cannot resolve and shall return
        an empty list if there are no items matching specified tokens. If the number of
        requested items is greater than MaxLimit, a TooManyItems fault shall be
        returned.
        """
        return self.operator.call("GetDoorInfo", Token=Token)

    def GetDoorList(self, Limit=None, StartReference=None):
        """This operation requests a list of all Door items provided by the device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer to section 4.8.3 in [Access Control Service
        Specification] for more details. The number of items returned shall not be
        greater than the Limit parameter.
        """
        return self.operator.call(
            "GetDoorList", Limit=Limit, StartReference=StartReference
        )

    def GetDoors(self, Token):
        """This operation requests a list of Door items matching the given tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching specified tokens. The device shall not return a
        fault in this case. If the number of requested items is greater than MaxLimit, a
        TooManyItems fault shall be returned.
        """
        return self.operator.call("GetDoors", Token=Token)

    def CreateDoor(self, Door):
        """This operation creates the specified door in the device.

        The token field of the Door structure shall be empty and the device shall
        allocate a token for the door. The allocated token shall be returned in the
        response. If the client sends any value in the token field, the device shall
        return InvalidArgVal as a generic fault code.
        """
        return self.operator.call("CreateDoor", Door=Door)

    def SetDoor(self, Door):
        """This method is used to synchronize a door in a client with the device.

        If a door with the specified token does not exist in the device, the door is
        created. If a door with the specified token exists, then the door is modified. A
        call to this method takes a door structure as input parameter. The token field
        of the Door structure shall not be empty. A device that signals support for the
        ClientSuppliedTokenSupported capability shall implement this command. If no
        token was specified in the request, the device shall return InvalidArgs as a
        generic fault code.
        """
        return self.operator.call("SetDoor", Door=Door)

    def ModifyDoor(self, Door):
        """This operation modifies the specified door.

        The token of the door to modify is specified in the token field of the Door
        structure and shall not be empty. All other fields in the structure shall
        overwrite the fields in the specified door. If no token was specified in the
        request, the device shall return InvalidArgs as a generic fault code.
        """
        return self.operator.call("ModifyDoor", Door=Door)

    def DeleteDoor(self, Token):
        """This operation deletes the specified door.

        If it is associated with one or more entities some devices may not be able to
        delete the door, and consequently a ReferenceInUse fault shall be generated. If
        no token was specified in the request, the device shall return InvalidArgs as a
        generic fault code.
        """
        return self.operator.call("DeleteDoor", Token=Token)

    def GetDoorState(self, Token):
        """This operation requests the state of a Door specified by the Token.

        A device implementing the Door Control service shall be capable of reporting the
        status of a door using a DoorState structure available from the GetDoorState
        command.
        """
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
        """This operation allows momentarily accessing a Door.

        It invokes the functionality typically used when a card holder presents a card
        to a card reader at the door and is granted access. The DoorMode shall change to
        Accessed state. Please refer to Accessed mode in section [DoorMode] for more
        details. The Door shall remain accessible for the defined time. When the time
        span elapses, the DoorMode shall change back to its previous state. If the
        request cannot be fulfilled, a Failure fault shall be returned. Please refer to
        section [DoorMode] for details about Door Modes restrictions. A device that
        signals support for Access capability for a particular Door instance shall
        implement this method. A device that signals support for AccessTimingOverride
        capability for a particular Door instance shall also provide optional timing
        parameters (AccessTime, OpenTooLongTime and PreAlarmTime) when performing
        AccessDoor command. The device shall take the best effort approach for
        parameters not supported, it must fallback to preconfigured time or limit the
        time to the closest supported time if the specified time is out of range.
        """
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
        """This operation allows locking a Door.

        The DoorMode shall change to Locked state. Please refer to Locked mode in
        section [DoorMode] for more details. A device that signals support for Lock
        capability for a particular Door instance shall implement this method. If the
        request cannot be fulfilled, a Failure fault shall be returned. Please refer to
        section [DoorMode] for more details about Door Modes restrictions.
        """
        return self.operator.call("LockDoor", Token=Token)

    def UnlockDoor(self, Token):
        """This operation allows unlocking a Door.

        The DoorMode shall change to Unlocked state. Please refer to Unlocked mode in
        section [DoorMode] for more details. A device that signals support for Unlock
        capability for a particular Door instance shall implement this method. If the
        request cannot be fulfilled, a Failure fault shall be returned. Please refer to
        section [DoorMode] for more details about Door Modes restrictions.
        """
        return self.operator.call("UnlockDoor", Token=Token)

    def BlockDoor(self, Token):
        """This operation allows blocking a Door and preventing momentary access
        (AccessDoor command).

        The DoorMode shall change to Blocked state. Please refer to Blocked mode in
        section [DoorMode] for more details. A device that signals support for Block
        capability for a particular Door instance shall implement this method. If the
        request cannot be fulfilled, a Failure fault shall be returned. Please refer to
        section [DoorMode] for more details about Door Modes restrictions.
        """
        return self.operator.call("BlockDoor", Token=Token)

    def LockDownDoor(self, Token):
        """This operation allows locking and preventing other actions until a
        LockDownRelease command is invoked.

        The DoorMode shall change to LockedDown state. Please refer to LockedDown mode
        in section [DoorMode] for more details. The device shall ignore other door
        control commands until a LockDownRelease command is performed. A device that
        signals support for LockDown capability for a particular Door instance shall
        implement this method. If a device supports DoubleLock capability for a
        particular Door instance, that operation may be engaged as well. If the request
        cannot be fulfilled, a Failure fault shall be returned. Please refer to section
        [DoorMode] for more details about Door Modes restrictions.
        """
        return self.operator.call("LockDownDoor", Token=Token)

    def LockDownReleaseDoor(self, Token):
        """This operation allows releasing the LockedDown state of a Door.

        The DoorMode shall change back to its previous/next state. It is not defined
        what the previous/next state shall be, but typically - Locked. This method shall
        only succeed if the current DoorMode is LockedDown.
        """
        return self.operator.call("LockDownReleaseDoor", Token=Token)

    def LockOpenDoor(self, Token):
        """This operation allows unlocking a Door and preventing other actions until
        LockOpenRelease method is invoked.

        The DoorMode shall change to LockedOpen state. Please refer to LockedOpen mode
        in section [DoorMode] for more details. The device shall ignore other door
        control commands until a LockOpenRelease command is performed. A device that
        signals support for LockOpen capability for a particular Door instance shall
        implement this method. If the request cannot be fulfilled, a Failure fault shall
        be returned. Please refer to section [DoorMode] for more details about Door
        Modes restrictions.
        """
        return self.operator.call("LockOpenDoor", Token=Token)

    def LockOpenReleaseDoor(self, Token):
        """This operation allows releasing the LockedOpen state of a Door.

        The DoorMode shall change state from the LockedOpen state back to its
        previous/next state. It is not defined what the previous/next state shall be,
        but typically - Unlocked. A device that signals support for LockOpen capability
        for a particular Door instance shall support this command. This method shall
        only succeed if the current DoorMode is LockedOpen.
        """
        return self.operator.call("LockOpenReleaseDoor", Token=Token)

    def DoubleLockDoor(self, Token):
        """This operation is used for securely locking a Door.

        A call to this method shall change DoorMode state to DoubleLocked. Please refer
        to DoubleLocked mode in section [DoorMode] for more details. A device that
        signals support for DoubleLock capability for a particular Door instance shall
        implement this method. Otherwise this method can be performed as a standard Lock
        operation (see [LockDoor command]). If the door has an extra lock that shall be
        locked as well. If the request cannot be fulfilled, a Failure fault shall be
        returned.
        """
        return self.operator.call("DoubleLockDoor", Token=Token)
