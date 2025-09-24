# onvif/services/security/jwt.py

from ...operator import ONVIFOperator
from ...utils import ONVIFWSDL


class JWT:
    def __init__(self, xaddr=None, **kwargs):
        definition = ONVIFWSDL.get_definition("jwt")
        self.operator = ONVIFOperator(
            definition["path"],
            binding=f"{{{definition['namespace']}}}{definition['binding']}",
            xaddr=xaddr,
            **kwargs,
        )

    def GetJWTConfiguration(self):
        return self.operator.call("GetJWTConfiguration")

    def SetJWTConfiguration(self, Configuration):
        return self.operator.call("SetJWTConfiguration", Configuration=Configuration)
