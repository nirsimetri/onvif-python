"""
Path: examples/direct_zeep.py
Author: @kaburagisec
Created: October 21, 2026

This script demonstrates how to invoke ONVIF operations using
the `zeep` library directly, without relying on the `onvif-python` module.
"""

from requests import Session
from requests.auth import HTTPDigestAuth
from zeep import Client, Settings
from zeep.plugins import HistoryPlugin
from zeep.transports import Transport

HOST = "192.168.69.249"
PORT = 80
USERNAME = "admin"
PASSWORD = "password"

WSDL = "https://www.onvif.org/ver10/device/wsdl/devicemgmt.wsdl"
ADDRESS = f"http://{HOST}:{PORT}/devicemgmt"

session = Session()
session.auth = HTTPDigestAuth(USERNAME, PASSWORD)

history = HistoryPlugin()

client = Client(
    wsdl=WSDL,
    transport=Transport(session=session, timeout=15),
    settings=Settings(strict=True, xml_huge_tree=True),
    plugins=[history],
)

service = client.create_service(
    "{http://www.onvif.org/ver10/device/wsdl}DeviceBinding",
    ADDRESS,
)

for schema_type in client.wsdl.types.types:
    if getattr(schema_type, "name", None) == "SystemCapabilities":
        print("Type:", schema_type)
        print("Attributes:")

        for attribute in schema_type.attributes:
            print(" ", attribute)

try:
    result = service.GetServiceCapabilities()

    print("=== Zeep parsed result ===")
    print(result)

    print("\n=== System capabilities ===")
    system = result.Capabilities.System

    print("FirmwareUpgrade:", system.FirmwareUpgrade)
    print("HttpFirmwareUpgrade:", system.HttpFirmwareUpgrade)

except Exception as exc:
    print(f"{type(exc).__name__}: {exc}")

finally:
    if history.last_received:
        print("\n=== Raw SOAP response ===")
        print(
            client.transport.binding_options
            if False
            else __import__("lxml.etree", fromlist=["etree"]).tostring(
                history.last_received["envelope"],
                pretty_print=True,
                encoding="unicode",
            )
        )
