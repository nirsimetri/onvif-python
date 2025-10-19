"""
Path: examples/pull_live_events.py
Author: @kaburagisec
Created: September 22, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device, creates a PullPoint subscription,
and continuously pulls live events for 15 minutes, printing event details to the console.
"""

import datetime
import xml.etree.ElementTree as ET
from onvif import ONVIFClient, CacheMode

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

client = ONVIFClient(
    HOST, PORT, USERNAME, PASSWORD, cache=CacheMode.NONE, capture_xml=True
)

# 1. Create PullPoint Subscription from Events service
subscription = client.events().CreatePullPointSubscription()
print("Subscription Response:\n", subscription)

# 2. Create PullPoint service instance with the Subscription reference
pullpoint = client.pullpoint(subscription)

# 3. Pull events for 15 minutes
end_time = datetime.datetime.now() + datetime.timedelta(minutes=15)
print("\n✅ Start pulling events for 15 minutes...")

while datetime.datetime.now() < end_time:
    try:
        # PT5S = 5 seconds timeout, MessageLimit=1000
        # Timeout can be adjusted as needed and in ISO 8601 format
        msgs = pullpoint.PullMessages(Timeout="PT5S", MessageLimit=1000)
        notifications = getattr(msgs, "NotificationMessage", None)

        if notifications:
            if not isinstance(notifications, list):
                notifications = [notifications]

            for n in notifications:
                # Extract Topic from raw XML using XMLCapturePlugin
                topic_val = None
                try:
                    # Get last raw response from XMLCapturePlugin
                    last_raw_xml = (
                        client.xml_plugin.last_received_xml
                        if client.xml_plugin
                        else None
                    )
                    if last_raw_xml is not None:
                        root = ET.fromstring(last_raw_xml)
                        topic_elems = root.findall(
                            ".//{http://docs.oasis-open.org/wsn/b-2}Topic"
                        )
                        # Index of current notification
                        idx = notifications.index(n)
                        if idx < len(topic_elems):
                            topic_val = topic_elems[idx].text
                except Exception as e:
                    print("⚠️ XMLCapturePlugin topic parse error:", e)

                # Extract Message (XML element)
                # After the patch (> v0.0.4), _value_1 is directly a list of Elements (not a dict)
                msg_elem = None
                if hasattr(n.Message, "_value_1") and n.Message._value_1:
                    # _value_1 is now a list of Elements, take the first one
                    if (
                        isinstance(n.Message._value_1, list)
                        and len(n.Message._value_1) > 0
                    ):
                        msg_elem = n.Message._value_1[0]
                    else:
                        msg_elem = n.Message._value_1

                if msg_elem is not None:
                    # Extract timestamp from UtcTime attribute
                    utc_str = msg_elem.get("UtcTime")
                    if utc_str:
                        ts_utc = datetime.datetime.fromisoformat(
                            utc_str.replace("Z", "+00:00")
                        )
                        ts = ts_utc.astimezone()
                    else:
                        ts = datetime.datetime.now().astimezone()

                    print("\n=== Event received @", ts, "===")

                    # print("PullMessages Response:\n", msgs)

                    print("Operation ->", msg_elem.get("PropertyOperation"))

                    print("Topic ->", topic_val)

                    # Extract <tt:Source>
                    source_tokens = []
                    for el in msg_elem.findall(
                        ".//{http://www.onvif.org/ver10/schema}Source/{http://www.onvif.org/ver10/schema}SimpleItem"
                    ):
                        name = el.get("Name")
                        value = el.get("Value")
                        source_tokens.append(f"{name}: {value}")
                    if source_tokens:
                        print("Source ->", ", ".join(source_tokens))

                    # Extract <tt:Data>
                    data_tokens = []
                    for el in msg_elem.findall(
                        ".//{http://www.onvif.org/ver10/schema}Data/{http://www.onvif.org/ver10/schema}SimpleItem"
                    ):
                        name = el.get("Name")
                        value = el.get("Value")
                        data_tokens.append(f"{name}: {value}")
                    if data_tokens:
                        print("Data ->", ", ".join(data_tokens))

                else:
                    print("\n-> Event without Message")
        else:
            print("\n-> 🔁 No new events.")
    except Exception as e:
        print("\n-> ❌ Error while pulling events:", e)

    # time.sleep(1)  # small delay between requests

print("\n✅ Finished: 15 minutes event pulling ended")
