# onvif/services/security/advancedsecurity.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL


class AdvancedSecurity:
    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("advancedsecurity")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            service_path="Security",  # fallback
            xaddr=xaddr,
            **kwargs,
        )

    def GetServiceCapabilities(self):
        return self.operator.call("GetServiceCapabilities")
