"""Schedule service implementation."""

from onvif.operator import ONVIFOperator
from onvif.utils.service import ONVIFService
from onvif.utils.wsdl import ONVIFWSDL


# pylint: disable=invalid-name,redefined-outer-name
class Schedule(ONVIFService):
    """Schedule service client.

    | Property | Details |
    | --- | --- |
    | **First introduced** | ONVIF Release 2.6 (June 2015) |
    | **Binding name** | `ScheduleBinding` (`ver10/schedule/wsdl/schedule.wsdl`) |
    | **Operations** | [schedule.wsdl](https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schedule/wsdl/schedule.wsdl) |
    | **Specification** | [Schedule.xml](https://developer.onvif.org/pub/specs/branches/development/doc/Schedule.xml) |
    """

    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("schedule")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Schedule",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        """This operation returns the capabilities of the schedule service."""
        return self.operator.call("GetServiceCapabilities")

    def GetScheduleState(self, Token):
        """This operation requests the ScheduleState for the schedule instance specified
        by the given token."""
        return self.operator.call("GetScheduleState", Token=Token)

    def GetScheduleInfo(self, Token):
        """This method returns a list of schedule info items, specified in the request.

        Only found schedules shall be returned, i.e., the returned numbers of elements
        can differ from the requested element. The device shall ignore tokens it cannot
        resolve and shall return an empty list if there are no items matching the
        specified tokens. If the number of requested items is greater than MaxLimit, a
        TooManyItems fault shall be returned.
        """
        return self.operator.call("GetScheduleInfo", Token=Token)

    def GetScheduleInfoList(self, Limit=None, StartReference=None):
        """This operation requests a list of all of ScheduleInfo items provided by the
        device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer Access Control Service Specification for more
        details. The number of items returned shall not be greater the Limit parameter.
        """
        return self.operator.call(
            "GetScheduleInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetSchedules(self, Token):
        """This operation returns the specified schedule item matching the given tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching the specified tokens. If the number of requested
        items is greater than MaxLimit, a TooManyItems fault shall be returned
        """
        return self.operator.call("GetSchedules", Token=Token)

    def GetScheduleList(self, Limit=None, StartReference=None):
        """This operation requests a list of all of Schedule items provided by the
        device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer Access Control Service Specification for more
        details. The number of items returned shall not be greater the Limit parameter.
        """
        return self.operator.call(
            "GetScheduleList", Limit=Limit, StartReference=StartReference
        )

    def CreateSchedule(self, Schedule):
        """This operation creates the specified schedule.

        The token field of the schedule structure shall be empty, the device shall
        allocate a token for the schedule. The allocated token shall be returned in the
        response. If the client sends any value in the token field, the device shall
        return InvalidArgVal as generic fault code.
        """
        return self.operator.call("CreateSchedule", Schedule=Schedule)

    def SetSchedule(self, Schedule):
        """This operation modifies or creates the specified schedule."""
        return self.operator.call("SetSchedule", Schedule=Schedule)

    def ModifySchedule(self, Schedule):
        """This operation modifies or updates the specified schedule."""
        return self.operator.call("ModifySchedule", Schedule=Schedule)

    def DeleteSchedule(self, Token):
        """This operation will delete the specified schedule.

        If it is associated with one or more entities some devices may not be able to
        delete the schedule, and consequently a ReferenceInUse fault shall be generated.
        """
        return self.operator.call("DeleteSchedule", Token=Token)

    def GetSpecialDayGroupInfo(self, Token):
        """This operation requests a list of SpecialDayGroupInfo items matching the
        given tokens.

        The device shall ignore tokens it cannot resolve and shall return an empty list
        if there are no items matching specified tokens. The device shall not return a
        fault in this case. If the number of requested items is greater than MaxLimit, a
        TooManyItems fault shall be returned.
        """
        return self.operator.call("GetSpecialDayGroupInfo", Token=Token)

    def GetSpecialDayGroupInfoList(self, Limit=None, StartReference=None):
        """This operation requests a list of all of SpecialDayGroupInfo items provided
        by the device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. The number of items returned shall not be greater than
        Limit parameter.
        """
        return self.operator.call(
            "GetSpecialDayGroupInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetSpecialDayGroups(self, Token):
        """This operation returns the specified special day group item matching the
        given token."""
        return self.operator.call("GetSpecialDayGroups", Token=Token)

    def GetSpecialDayGroupList(self, Limit=None, StartReference=None):
        """This operation requests a list of all of SpecialDayGroupList items provided
        by the device.

        A call to this method shall return a StartReference when not all data is
        returned and more data is available. The reference shall be valid for retrieving
        the next set of data. Please refer Access Control Service Specification for more
        details. The number of items returned shall not be greater the Limit parameter.
        """
        return self.operator.call(
            "GetSpecialDayGroupList", Limit=Limit, StartReference=StartReference
        )

    def CreateSpecialDayGroup(self, SpecialDayGroup):
        """This operation creates the specified special day group.

        The token field of the SpecialDayGroup structure shall be empty, the device
        shall allocate a token for the special day group. The allocated token shall be
        returned in the response. If there is any value in the token field, the device
        shall return InvalidArgVal as generic fault code.
        """
        return self.operator.call(
            "CreateSpecialDayGroup", SpecialDayGroup=SpecialDayGroup
        )

    def SetSpecialDayGroup(self, SpecialDayGroup):
        """This operation modifies or creates the specified special day group."""
        return self.operator.call("SetSpecialDayGroup", SpecialDayGroup=SpecialDayGroup)

    def ModifySpecialDayGroup(self, SpecialDayGroup):
        """This operation updates the specified special day group."""
        return self.operator.call(
            "ModifySpecialDayGroup", SpecialDayGroup=SpecialDayGroup
        )

    def DeleteSpecialDayGroup(self, Token):
        """This method deletes the specified special day group.

        If it is associated with one or more schedules some devices may not be able to
        delete the special day group, and consequently a ReferenceInUse fault must be
        generated.
        """
        return self.operator.call("DeleteSpecialDayGroup", Token=Token)
