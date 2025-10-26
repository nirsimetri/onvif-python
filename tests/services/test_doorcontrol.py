from onvif.services import DoorControl
from base_service_test import ONVIFServiceTestBase


class TestDoorControlWSDLCompliance(ONVIFServiceTestBase):
    """Test that DoorControl service implementation matches WSDL specification."""

    # Service-specific configuration
    SERVICE_CLASS = DoorControl
    SERVICE_NAME = "doorcontrol"
    WSDL_PATH_COMPONENTS = ["ver10", "pacs", "doorcontrol.wsdl"]
    BINDING_NAME = "DoorControlBinding"
    NAMESPACE_PREFIX = "tdc"
    SERVICE_NAMESPACE = "http://www.onvif.org/ver10/doorcontrol/wsdl"
    XADDR_PATH = "/onvif/DoorControl"

    def test_specific_methods_implementation(self):
        """Test specific important methods are correctly implemented."""
        test_cases = [
            {"method": "GetServiceCapabilities"},
            {
                "method": "GetDoorInfoList",
                "params": {"Limit": 10, "StartReference": "ref1"},
            },
            {"method": "GetDoorInfo", "params": {"Token": "door1"}},
            {
                "method": "GetDoorList",
                "params": {"Limit": 20, "StartReference": "ref2"},
            },
            {"method": "GetDoors", "params": {"Token": "door2"}},
            {
                "method": "CreateDoor",
                "params": {"Door": {"Token": "newdoor", "Name": "Main Door"}},
            },
            {
                "method": "SetDoor",
                "params": {"Door": {"Token": "door3", "Name": "Updated Door"}},
            },
            {
                "method": "ModifyDoor",
                "params": {"Door": {"Token": "door4", "Name": "Modified Door"}},
            },
            {"method": "DeleteDoor", "params": {"Token": "door5"}},
            {"method": "GetDoorState", "params": {"Token": "door6"}},
            {
                "method": "AccessDoor",
                "params": {
                    "Token": "door7",
                    "UseExtendedTime": True,
                    "AccessTime": "PT10S",
                    "OpenTooLongTime": "PT30S",
                    "PreAlarmTime": "PT5S",
                    "Extension": {"CustomField": "value"},
                },
            },
            {"method": "LockDoor", "params": {"Token": "door8"}},
            {"method": "UnlockDoor", "params": {"Token": "door9"}},
            {"method": "BlockDoor", "params": {"Token": "door10"}},
            {"method": "LockDownDoor", "params": {"Token": "door11"}},
            {"method": "LockDownReleaseDoor", "params": {"Token": "door12"}},
            {"method": "LockOpenDoor", "params": {"Token": "door13"}},
            {"method": "LockOpenReleaseDoor", "params": {"Token": "door14"}},
            {"method": "DoubleLockDoor", "params": {"Token": "door15"}},
        ]
        self.run_specific_methods_tests(test_cases)

    def test_parameter_forwarding(self):
        """Test that parameters are correctly forwarded to operator.call()."""
        test_cases = [
            {
                "method": "GetDoorInfoList",
                "params": {"Limit": 5, "StartReference": "start1"},
            },
            {
                "method": "GetDoorInfo",
                "params": {"Token": "token1"},
            },
            {
                "method": "GetDoorList",
                "params": {"Limit": 15, "StartReference": "start2"},
            },
            {
                "method": "GetDoors",
                "params": {"Token": "token2"},
            },
            {
                "method": "CreateDoor",
                "params": {"Door": {"Token": "newdoor1", "Name": "New Door"}},
            },
            {
                "method": "SetDoor",
                "params": {"Door": {"Token": "door1", "Name": "Set Door"}},
            },
            {
                "method": "ModifyDoor",
                "params": {"Door": {"Token": "door2", "Name": "Modify Door"}},
            },
            {
                "method": "DeleteDoor",
                "params": {"Token": "token3"},
            },
            {
                "method": "GetDoorState",
                "params": {"Token": "token4"},
            },
            {
                "method": "AccessDoor",
                "params": {
                    "Token": "token5",
                    "UseExtendedTime": False,
                    "AccessTime": "PT15S",
                    "OpenTooLongTime": "PT20S",
                    "PreAlarmTime": "PT3S",
                    "Extension": {"Key": "Value"},
                },
            },
            {
                "method": "LockDoor",
                "params": {"Token": "token6"},
            },
            {
                "method": "UnlockDoor",
                "params": {"Token": "token7"},
            },
            {
                "method": "BlockDoor",
                "params": {"Token": "token8"},
            },
            {
                "method": "LockDownDoor",
                "params": {"Token": "token9"},
            },
            {
                "method": "LockDownReleaseDoor",
                "params": {"Token": "token10"},
            },
            {
                "method": "LockOpenDoor",
                "params": {"Token": "token11"},
            },
            {
                "method": "LockOpenReleaseDoor",
                "params": {"Token": "token12"},
            },
            {
                "method": "DoubleLockDoor",
                "params": {"Token": "token13"},
            },
        ]
        self.run_parameter_forwarding_tests(test_cases)
