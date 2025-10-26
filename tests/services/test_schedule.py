from onvif.services import Schedule
from base_service_test import ONVIFServiceTestBase


class TestScheduleWSDLCompliance(ONVIFServiceTestBase):
    """Test that Schedule service implementation matches WSDL specification."""

    # Service configuration
    SERVICE_CLASS = Schedule
    SERVICE_NAME = "schedule"
    WSDL_PATH_COMPONENTS = ["ver10", "schedule", "wsdl", "schedule.wsdl"]
    BINDING_NAME = "ScheduleBinding"
    NAMESPACE_PREFIX = "tsc"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/schedule/wsdl"
    XADDR_PATH = "/onvif/Schedule"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities", "params": {}},
            {"method": "GetScheduleState", "params": {"Token": "schedule1"}},
            {"method": "GetScheduleInfo", "params": {"Token": "schedule2"}},
            {
                "method": "GetScheduleInfoList",
                "params": {"Limit": 10, "StartReference": "ref1"},
            },
            {"method": "GetSchedules", "params": {"Token": "schedule3"}},
            {
                "method": "CreateSchedule",
                "params": {
                    "Schedule": {"Token": "new_schedule", "Name": "Daily Schedule"}
                },
            },
            {
                "method": "SetSchedule",
                "params": {
                    "Schedule": {"Token": "schedule4", "Name": "Updated Schedule"}
                },
            },
            {"method": "DeleteSchedule", "params": {"Token": "schedule5"}},
            {"method": "GetSpecialDayGroupInfo", "params": {"Token": "daygroup1"}},
            {
                "method": "CreateSpecialDayGroup",
                "params": {
                    "SpecialDayGroup": {"Token": "new_group", "Name": "Holidays"}
                },
            },
            {"method": "DeleteSpecialDayGroup", "params": {"Token": "daygroup2"}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetScheduleState",
                "params": {"Token": "sch1"},
            },
            {
                "method": "GetScheduleInfo",
                "params": {"Token": "sch2"},
            },
            {
                "method": "GetScheduleInfoList",
                "params": {"Limit": 20, "StartReference": "ref2"},
            },
            {
                "method": "GetSchedules",
                "params": {"Token": "sch3"},
            },
            {
                "method": "GetScheduleList",
                "params": {"Limit": 15, "StartReference": "ref3"},
            },
            {
                "method": "CreateSchedule",
                "params": {"Schedule": {"Token": "new_sch", "Name": "Weekly Schedule"}},
            },
            {
                "method": "SetSchedule",
                "params": {"Schedule": {"Token": "sch4", "Name": "Modified Schedule"}},
            },
            {
                "method": "ModifySchedule",
                "params": {"Schedule": {"Token": "sch5", "Name": "Altered Schedule"}},
            },
            {
                "method": "DeleteSchedule",
                "params": {"Token": "sch6"},
            },
            {
                "method": "GetSpecialDayGroupInfo",
                "params": {"Token": "group1"},
            },
            {
                "method": "GetSpecialDayGroupInfoList",
                "params": {"Limit": 25, "StartReference": "ref4"},
            },
            {
                "method": "CreateSpecialDayGroup",
                "params": {
                    "SpecialDayGroup": {"Token": "new_group", "Name": "Weekends"}
                },
            },
            {
                "method": "SetSpecialDayGroup",
                "params": {
                    "SpecialDayGroup": {"Token": "group2", "Name": "Updated Group"}
                },
            },
            {
                "method": "DeleteSpecialDayGroup",
                "params": {"Token": "group3"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
