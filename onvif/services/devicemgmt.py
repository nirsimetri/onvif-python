# onvif/services/devicemgmt.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class Device(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Core
        # - DeviceBinding (ver10/device/wsdl/devicemgmt.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/device/wsdl/devicemgmt.wsdl

        definition = ONVIFWSDL.get_definition("devicemgmt")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="device_service",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServices(self, IncludeCapability):
        return self.operator.call("GetServices", IncludeCapability=IncludeCapability)

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def GetDeviceInformation(self):
        return self.operator.call("GetDeviceInformation")

    def SetSystemDateAndTime(
        self, DateTimeType, DaylightSavings, TimeZone=None, UTCDateTime=None
    ):
        return self.operator.call(
            "SetSystemDateAndTime",
            DateTimeType=DateTimeType,
            DaylightSavings=DaylightSavings,
            TimeZone=TimeZone,
            UTCDateTime=UTCDateTime,
        )

    def GetSystemDateAndTime(self):
        return self.operator.call("GetSystemDateAndTime")

    def SetSystemFactoryDefault(self, FactoryDefault):
        return self.operator.call(
            "SetSystemFactoryDefault", FactoryDefault=FactoryDefault
        )

    def UpgradeSystemFirmware(self, Firmware):
        return self.operator.call("UpgradeSystemFirmware", Firmware=Firmware)

    def SystemReboot(self):
        return self.operator.call("SystemReboot")

    def RestoreSystem(self, BackupFiles):
        return self.operator.call("RestoreSystem", BackupFiles=BackupFiles)

    def GetSystemBackup(self):
        return self.operator.call("GetSystemBackup")

    def GetSystemLog(self, LogType):
        return self.operator.call("GetSystemLog", LogType=LogType)

    def GetSystemSupportInformation(self):
        return self.operator.call("GetSystemSupportInformation")

    def GetScopes(self):
        return self.operator.call("GetScopes")

    def SetScopes(self, Scopes):
        return self.operator.call("SetScopes", Scopes=Scopes)

    def AddScopes(self, ScopeItem):
        return self.operator.call("AddScopes", ScopeItem=ScopeItem)

    def RemoveScopes(self, ScopeItem):
        return self.operator.call("RemoveScopes", ScopeItem=ScopeItem)

    def GetDiscoveryMode(self):
        return self.operator.call("GetDiscoveryMode")

    def SetDiscoveryMode(self, DiscoveryMode):
        return self.operator.call("SetDiscoveryMode", DiscoveryMode=DiscoveryMode)

    def GetRemoteDiscoveryMode(self):
        return self.operator.call("GetRemoteDiscoveryMode")

    def SetRemoteDiscoveryMode(self, RemoteDiscoveryMode):
        return self.operator.call(
            "SetRemoteDiscoveryMode", RemoteDiscoveryMode=RemoteDiscoveryMode
        )

    def GetDPAddresses(self):
        return self.operator.call("GetDPAddresses")

    def GetEndpointReference(self):
        return self.operator.call("GetEndpointReference")

    def GetRemoteUser(self):
        return self.operator.call("GetRemoteUser")

    def SetRemoteUser(self, RemoteUser=None):
        return self.operator.call("SetRemoteUser", RemoteUser=RemoteUser)

    def GetUsers(self):
        return self.operator.call("GetUsers")

    def CreateUsers(self, User):
        return self.operator.call("CreateUsers", User=User)

    def DeleteUsers(self, Username):
        return self.operator.call("DeleteUsers", Username=Username)

    def SetUser(self, User):
        return self.operator.call("SetUser", User=User)

    def GetWsdlUrl(self):
        return self.operator.call("GetWsdlUrl")

    def GetPasswordComplexityOptions(self):
        return self.operator.call("GetPasswordComplexityOptions")

    def GetPasswordComplexityConfiguration(self):
        return self.operator.call("GetPasswordComplexityConfiguration")

    def SetPasswordComplexityConfiguration(
        self,
        MinLen=None,
        Uppercase=None,
        Number=None,
        SpecialChars=None,
        BlockUsernameOccurrence=None,
        PolicyConfigurationLocked=None,
    ):
        return self.operator.call(
            "SetPasswordComplexityConfiguration",
            MinLen=MinLen,
            Uppercase=Uppercase,
            Number=Number,
            SpecialChars=SpecialChars,
            BlockUsernameOccurrence=BlockUsernameOccurrence,
            PolicyConfigurationLocked=PolicyConfigurationLocked,
        )

    def GetPasswordHistoryConfiguration(self):
        return self.operator.call("GetPasswordHistoryConfiguration")

    def SetPasswordHistoryConfiguration(self, Enabled, Length):
        return self.operator.call(
            "SetPasswordHistoryConfiguration", Enabled=Enabled, Length=Length
        )

    def GetAuthFailureWarningOptions(self):
        return self.operator.call("GetAuthFailureWarningOptions")

    def GetAuthFailureWarningConfiguration(self):
        return self.operator.call("GetAuthFailureWarningConfiguration")

    def SetAuthFailureWarningConfiguration(
        self, Enabled, MonitorPeriod, MaxAuthFailures
    ):
        return self.operator.call(
            "SetAuthFailureWarningConfiguration",
            Enabled=Enabled,
            MonitorPeriod=MonitorPeriod,
            MaxAuthFailures=MaxAuthFailures,
        )

    def GetCapabilities(self, Category=None):
        return self.operator.call("GetCapabilities", Category=Category)

    def SetDPAddresses(self, DPAddress=None):
        return self.operator.call("SetDPAddresses", DPAddress=DPAddress)

    def GetHostname(self):
        return self.operator.call("GetHostname")

    def SetHostname(self, Name):
        return self.operator.call("SetHostname", Name=Name)

    def SetHostnameFromDHCP(self, FromDHCP):
        return self.operator.call("SetHostnameFromDHCP", FromDHCP=FromDHCP)

    def GetDNS(self):
        return self.operator.call("GetDNS")

    def SetDNS(self, FromDHCP, SearchDomain=None, DNSManual=None):
        return self.operator.call(
            "SetDNS", FromDHCP=FromDHCP, SearchDomain=SearchDomain, DNSManual=DNSManual
        )

    def GetNTP(self):
        return self.operator.call("GetNTP")

    def SetNTP(self, FromDHCP, NTPManual=None):
        return self.operator.call("SetNTP", FromDHCP=FromDHCP, NTPManual=NTPManual)

    def GetDynamicDNS(self):
        return self.operator.call("GetDynamicDNS")

    def SetDynamicDNS(self, Type, Name=None, TTL=None):
        return self.operator.call("SetDynamicDNS", Type=Type, Name=Name, TTL=TTL)

    def GetNetworkInterfaces(self):
        return self.operator.call("GetNetworkInterfaces")

    def SetNetworkInterfaces(self, InterfaceToken, NetworkInterface):
        return self.operator.call(
            "SetNetworkInterfaces",
            InterfaceToken=InterfaceToken,
            NetworkInterface=NetworkInterface,
        )

    def GetNetworkProtocols(self):
        return self.operator.call("GetNetworkProtocols")

    def SetNetworkProtocols(self, NetworkProtocols):
        return self.operator.call(
            "SetNetworkProtocols", NetworkProtocols=NetworkProtocols
        )

    def GetNetworkDefaultGateway(self):
        return self.operator.call("GetNetworkDefaultGateway")

    def SetNetworkDefaultGateway(self, IPv4Address=None, IPv6Address=None):
        return self.operator.call(
            "SetNetworkDefaultGateway", IPv4Address=IPv4Address, IPv6Address=IPv6Address
        )

    def GetZeroConfiguration(self):
        return self.operator.call("GetZeroConfiguration")

    def SetZeroConfiguration(self, InterfaceToken, Enabled):
        return self.operator.call(
            "SetZeroConfiguration", InterfaceToken=InterfaceToken, Enabled=Enabled
        )

    def GetIPAddressFilter(self):
        return self.operator.call("GetIPAddressFilter")

    def SetIPAddressFilter(self, IPAddressFilter):
        return self.operator.call("SetIPAddressFilter", IPAddressFilter=IPAddressFilter)

    def AddIPAddressFilter(self, IPAddressFilter):
        return self.operator.call("AddIPAddressFilter", IPAddressFilter=IPAddressFilter)

    def RemoveIPAddressFilter(self, IPAddressFilter):
        return self.operator.call(
            "RemoveIPAddressFilter", IPAddressFilter=IPAddressFilter
        )

    def GetAccessPolicy(self):
        return self.operator.call("GetAccessPolicy")

    def SetAccessPolicy(self, PolicyFile):
        return self.operator.call("SetAccessPolicy", PolicyFile=PolicyFile)

    def CreateCertificate(
        self, CertificateID=None, Subject=None, ValidNotBefore=None, ValidNotAfter=None
    ):
        return self.operator.call(
            "CreateCertificate",
            CertificateID=CertificateID,
            Subject=Subject,
            ValidNotBefore=ValidNotBefore,
            ValidNotAfter=ValidNotAfter,
        )

    def GetCertificates(self):
        return self.operator.call("GetCertificates")

    def GetCertificatesStatus(self):
        return self.operator.call("GetCertificatesStatus")

    def SetCertificatesStatus(self, CertificateStatus=None):
        return self.operator.call(
            "SetCertificatesStatus", CertificateStatus=CertificateStatus
        )

    def DeleteCertificates(self, CertificateID):
        return self.operator.call("DeleteCertificates", CertificateID=CertificateID)

    def GetPkcs10Request(self, CertificateID, Subject=None, Attributes=None):
        return self.operator.call(
            "GetPkcs10Request",
            CertificateID=CertificateID,
            Subject=Subject,
            Attributes=Attributes,
        )

    def LoadCertificates(self, NVTCertificate):
        return self.operator.call("LoadCertificates", NVTCertificate=NVTCertificate)

    def GetClientCertificateMode(self):
        return self.operator.call("GetClientCertificateMode")

    def SetClientCertificateMode(self, Enabled):
        return self.operator.call("SetClientCertificateMode", Enabled=Enabled)

    def GetRelayOutputs(self):
        return self.operator.call("GetRelayOutputs")

    def SetRelayOutputSettings(self, RelayOutputToken, Properties):
        return self.operator.call(
            "SetRelayOutputSettings",
            RelayOutputToken=RelayOutputToken,
            Properties=Properties,
        )

    def SetRelayOutputState(self, RelayOutputToken, LogicalState):
        return self.operator.call(
            "SetRelayOutputState",
            RelayOutputToken=RelayOutputToken,
            LogicalState=LogicalState,
        )

    def SendAuxiliaryCommand(self, AuxiliaryCommand):
        return self.operator.call(
            "SendAuxiliaryCommand", AuxiliaryCommand=AuxiliaryCommand
        )

    def GetCACertificates(self):
        return self.operator.call("GetCACertificates")

    def LoadCertificateWithPrivateKey(self, CertificateWithPrivateKey):
        return self.operator.call(
            "LoadCertificateWithPrivateKey",
            CertificateWithPrivateKey=CertificateWithPrivateKey,
        )

    def GetCertificateInformation(self, CertificateID):
        return self.operator.call(
            "GetCertificateInformation", CertificateID=CertificateID
        )

    def LoadCACertificates(self, CACertificate):
        return self.operator.call("LoadCACertificates", CACertificate=CACertificate)

    def CreateDot1XConfiguration(self, Dot1XConfiguration):
        return self.operator.call(
            "CreateDot1XConfiguration", Dot1XConfiguration=Dot1XConfiguration
        )

    def SetDot1XConfiguration(self, Dot1XConfiguration):
        return self.operator.call(
            "SetDot1XConfiguration", Dot1XConfiguration=Dot1XConfiguration
        )

    def GetDot1XConfiguration(self, Dot1XConfigurationToken):
        return self.operator.call(
            "GetDot1XConfiguration", Dot1XConfigurationToken=Dot1XConfigurationToken
        )

    def GetDot1XConfigurations(self):
        return self.operator.call("GetDot1XConfigurations")

    def DeleteDot1XConfiguration(self, Dot1XConfigurationToken=None):
        return self.operator.call(
            "DeleteDot1XConfiguration", Dot1XConfigurationToken=Dot1XConfigurationToken
        )

    def GetDot11Capabilities(self):
        return self.operator.call("GetDot11Capabilities")

    def GetDot11Status(self, InterfaceToken):
        return self.operator.call("GetDot11Status", InterfaceToken=InterfaceToken)

    def ScanAvailableDot11Networks(self, InterfaceToken):
        return self.operator.call(
            "ScanAvailableDot11Networks", InterfaceToken=InterfaceToken
        )

    def GetSystemUris(self):
        return self.operator.call("GetSystemUris")

    def StartFirmwareUpgrade(self):
        return self.operator.call("StartFirmwareUpgrade")

    def StartSystemRestore(self):
        return self.operator.call("StartSystemRestore")

    def GetStorageConfigurations(self):
        return self.operator.call("GetStorageConfigurations")

    def CreateStorageConfiguration(self, StorageConfiguration):
        return self.operator.call(
            "CreateStorageConfiguration", StorageConfiguration=StorageConfiguration
        )

    def GetStorageConfiguration(self, Token):
        return self.operator.call("GetStorageConfiguration", Token=Token)

    def SetStorageConfiguration(self, StorageConfiguration):
        return self.operator.call(
            "SetStorageConfiguration", StorageConfiguration=StorageConfiguration
        )

    def DeleteStorageConfiguration(self, Token):
        return self.operator.call("DeleteStorageConfiguration", Token=Token)

    def GetGeoLocation(self):
        return self.operator.call("GetGeoLocation")

    def SetGeoLocation(self, Location):
        return self.operator.call("SetGeoLocation", Location=Location)

    def DeleteGeoLocation(self, Location):
        return self.operator.call("DeleteGeoLocation", Location=Location)

    def SetHashingAlgorithm(self, Algorithm):
        return self.operator.call("SetHashingAlgorithm", Algorithm=Algorithm)

    def UpgradeFirmware(self, Version):
        return self.operator.call("UpgradeFirmware", Version=Version)
