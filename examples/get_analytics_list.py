"""
Path: examples/get_analytics_list.py
Author: @kaburagisec
Created: September 18, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device and retrieves the list of supported
analytics modules using the Analytics service.
"""

from onvif import ONVIFClient

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

try:
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
    profile = client.media().GetProfiles()[0]  # use the first profile
    services = client.analytics().GetSupportedAnalyticsModules(
        ConfigurationToken=profile.VideoAnalyticsConfiguration.token
    )
    print(services)
except Exception as e:
    print(e)
