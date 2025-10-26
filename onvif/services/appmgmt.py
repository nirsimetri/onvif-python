# onvif/services/appmgmt.py

from ..operator import ONVIFOperator
from ..utils import ONVIFWSDL, ONVIFService


class AppManagement(ONVIFService):
    def __init__(self, xaddr=None, **kwargs):
        # References:
        # - ONVIF Release 19.12 (December 2019) Release Notes
        # - AppManagementBinding (ver10/appmgmt/wsdl/appmgmt.wsdl)
        # - Operations: https://developer.onvif.org/pub/specs/branches/development/wsdl/ver10/appmgmt/wsdl/appmgmt.wsdl

        definition = ONVIFWSDL.get_definition("appmgmt")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="AppManagement",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")

    def Uninstall(self, AppID):
        return self.operator.call("Uninstall", AppID=AppID)

    def GetInstalledApps(self):
        return self.operator.call("GetInstalledApps")

    def GetAppsInfo(self, AppID=None):
        return self.operator.call("GetAppsInfo", AppID=AppID)

    def Activate(self, AppID):
        return self.operator.call("Activate", AppID=AppID)

    def Deactivate(self, AppID):
        return self.operator.call("Deactivate", AppID=AppID)

    def InstallLicense(self, License, AppID=None):
        return self.operator.call("InstallLicense", AppID=AppID, License=License)

    def GetDeviceId(self):
        return self.operator.call("GetDeviceId")
