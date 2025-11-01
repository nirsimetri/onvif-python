"""
Path: examples/set_device_time.py
Author: @kaburagisec
Created: November 01, 2025
Tested devices: TP-Link Tapo C210 (https://www.tp-link.com/en/home-networking/cloud-camera/tapo-c210/)

This example demonstrates how to get and set system date and time on an ONVIF device.

"""

from datetime import datetime
from onvif import ONVIFClient

HOST = "192.168.1.14"
PORT = 2020
USERNAME = "admintapo"
PASSWORD = "admin123"

try:
    client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD)
    device_service = client.devicemgmt()

    system_date_time = device_service.GetSystemDateAndTime()
    print(f"Current System Date and Time: {system_date_time}\n")

    # With default arguments passing, sets the device time to the current local time
    device_service.SetSystemDateAndTime(
        DateTimeType="NTP",  # enum { 'Manual', 'NTP' }
        DaylightSavings=False,
        TimeZone=system_date_time.TimeZone,
        UTCDateTime=system_date_time.UTCDateTime,
    )

    # Optional
    # Or with type() helper method
    time_params = device_service.type("SetSystemDateAndTime")
    time_params.DateTimeType = "Manual"  # enum { 'Manual', 'NTP' }
    time_params.DaylightSavings = False
    time_params.TimeZone.TZ = "UTC+02:00"
    now = datetime.now()
    time_params.UTCDateTime.Date.Year = now.year
    time_params.UTCDateTime.Date.Month = now.month
    time_params.UTCDateTime.Date.Day = now.day
    time_params.UTCDateTime.Time.Hour = now.hour
    time_params.UTCDateTime.Time.Minute = now.minute
    time_params.UTCDateTime.Time.Second = now.second
    device_service.SetSystemDateAndTime(time_params)

    system_date_time_after = device_service.GetSystemDateAndTime()
    print(f"Updated System Date and Time: {system_date_time_after}\n")
except Exception as e:
    print(e)
