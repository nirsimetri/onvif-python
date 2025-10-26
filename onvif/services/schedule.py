# onvif/services/schedule.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Schedule(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 2.6 (June 2015) Release Notes
        # - ScheduleBinding (ver10/schedule/wsdl/schedule.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/schedule/wsdl/schedule.wsdl

        definition = ONVIFWSDL.get_definition("schedule")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Schedule",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetScheduleState(self, Token):
        return self.operator.call("GetScheduleState", Token=Token)

    def GetScheduleInfo(self, Token):
        return self.operator.call("GetScheduleInfo", Token=Token)

    def GetScheduleInfoList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetScheduleInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetSchedules(self, Token):
        return self.operator.call("GetSchedules", Token=Token)

    def GetScheduleList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetScheduleList", Limit=Limit, StartReference=StartReference
        )

    def CreateSchedule(self, Schedule):
        return self.operator.call("CreateSchedule", Schedule=Schedule)

    def SetSchedule(self, Schedule):
        return self.operator.call("SetSchedule", Schedule=Schedule)

    def ModifySchedule(self, Schedule):
        return self.operator.call("ModifySchedule", Schedule=Schedule)

    def DeleteSchedule(self, Token):
        return self.operator.call("DeleteSchedule", Token=Token)

    def GetSpecialDayGroupInfo(self, Token):
        return self.operator.call("GetSpecialDayGroupInfo", Token=Token)

    def GetSpecialDayGroupInfoList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetSpecialDayGroupInfoList", Limit=Limit, StartReference=StartReference
        )

    def GetSpecialDayGroups(self, Token):
        return self.operator.call("GetSpecialDayGroups", Token=Token)

    def GetSpecialDayGroupList(self, Limit=None, StartReference=None):
        return self.operator.call(
            "GetSpecialDayGroupList", Limit=Limit, StartReference=StartReference
        )

    def CreateSpecialDayGroup(self, SpecialDayGroup):
        return self.operator.call(
            "CreateSpecialDayGroup", SpecialDayGroup=SpecialDayGroup
        )

    def SetSpecialDayGroup(self, SpecialDayGroup):
        return self.operator.call("SetSpecialDayGroup", SpecialDayGroup=SpecialDayGroup)

    def ModifySpecialDayGroup(self, SpecialDayGroup):
        return self.operator.call(
            "ModifySpecialDayGroup", SpecialDayGroup=SpecialDayGroup
        )

    def DeleteSpecialDayGroup(self, Token):
        return self.operator.call("DeleteSpecialDayGroup", Token=Token)
