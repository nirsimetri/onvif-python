"""
Path: examples/pull_live_events.py
Author: @kaburagisec
Created: September 22, 2025
Tested devices: EZVIZ H8C (https://www.ezviz.com/inter/product/h8c/43162)

This script connects to an ONVIF-compliant device, creates a PullPoint subscription,
and continuously pulls live events for 10 minutes, printing event details to the console.
"""

import datetime
import xml.etree.ElementTree as ET
from zeep.plugins import HistoryPlugin
from onvif import ONVIFClient, CacheMode

HOST = "192.168.1.3"
PORT = 80
USERNAME = "admin"
PASSWORD = "admin123"

client = ONVIFClient(HOST, PORT, USERNAME, PASSWORD, cache=CacheMode.NONE)

# 1. Create PullPoint Subscription from Events service
subscription = client.events().CreatePullPointSubscription()
print("Subscription Response:\n", subscription)

# 2. Create PullPoint service instance with the Subscription reference
pullpoint = client.pullpoint(subscription)

# Inject HistoryPlugin to zeep client if available
history_plugin = HistoryPlugin()
if (
    hasattr(pullpoint, "operator")
    and hasattr(pullpoint.operator, "client")
    and hasattr(pullpoint.operator.client, "plugins")
):
    pullpoint.operator.client.plugins.append(history_plugin)

# 3. Pull events for 10 minutes
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
                # Extract Topic from raw XML using ElementTree
                topic_val = None
                try:
                    # Get last raw response from HistoryPlugin
                    last_raw_xml = (
                        history_plugin.last_received["envelope"]
                        if hasattr(history_plugin, "last_received")
                        and "envelope" in history_plugin.last_received
                        else None
                    )
                    if last_raw_xml is not None:
                        # If lxml.etree._Element, convert to string first
                        if hasattr(last_raw_xml, "tag"):
                            xml_str = ET.tostring(last_raw_xml, encoding="utf-8")
                        else:
                            xml_str = last_raw_xml
                        root = ET.fromstring(xml_str)
                        topic_elems = root.findall(
                            ".//{http://docs.oasis-open.org/wsn/b-2}Topic"
                        )
                        # Index of current notification
                        idx = notifications.index(n)
                        if idx < len(topic_elems):
                            topic_val = topic_elems[idx].text
                except Exception as e:
                    print("⚠️ HistoryPlugin topic parse error:", e)

                # Extract Message (XML element)
                # After the patch, _value_1 is directly a list of Elements (not a dict)
                msg_elem = None
                if hasattr(n.Message, "_value_1") and n.Message._value_1:
                    # _value_1 is now a list of Elements, take the first one
                    if isinstance(n.Message._value_1, list) and len(n.Message._value_1) > 0:
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

                    # Print raw XML of the event
                    # try:
                    # raw_xml = ET.tostring(msg_elem, encoding="unicode")
                    # print("Raw XML:\n", raw_xml)
                    # except Exception as ex:
                    # print("Could not print raw XML:", ex)
                else:
                    print("\n-> Event without Message")
        else:
            print("\n-> 🔁 No new events.")
    except Exception as e:
        print("\n-> ❌ Error while pulling events:", e)

    # time.sleep(1)  # small delay between requests

print("\n✅ Finished: 15 minutes event pulling ended")
