#!/usr/bin/python3

import json
import re
import ssl
import time
from datetime import datetime
import logging
import schedule
import os
import urllib3

# Modem url
url = os.environ["MODEM_URL"]

# Influx settings
influx = os.environ["USE_INFLUX"]
influx_database = os.environ["INFLUX_DATABASE"]
influx_server = os.environ["INFLUX_SERVER"]
influx_port = os.environ["INFLUX_PORT"]
influx_user = os.environ["INFLUX_USER"]
influx_password = os.environ["INFLUX_PASSWORD"]

# MQTT
mqtt = os.environ["USE_MQTT"]
mqtt_client = os.environ["MQTT_CLIENT_ID"]
mqtt_server = os.environ["MQTT_SERVER"]
mqtt_username = os.environ["MQTT_USERNAME"]
mqtt_password = os.environ["MQTT_PASSWORD"]

def do_work():

    # Ignore certificates warning
    urllib3.disable_warnings()
    http = urllib3.PoolManager(cert_reqs=ssl.CERT_NONE)

    # Get url
    response = http.request("GET", url)

    # Get current time
    current_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    decode = response.data.decode("utf-8")

    # Replace oid string with names
    decode = re.sub("1.3.6.1.2.1.10.127.1.1.1.1.1", "docsIfDownChannelId", decode)
    decode = re.sub(
        "1.3.6.1.2.1.10.127.1.1.1.1.2", "docsIfDownChannelFrequency", decode
    )
    decode = re.sub(
        "1.3.6.1.2.1.10.127.1.1.1.1.4", "docsIfDownChannelModulation", decode
    )
    decode = re.sub("1.3.6.1.2.1.10.127.1.1.1.1.6", "docsIfDownChannelPower", decode)
    decode = re.sub("1.3.6.1.2.1.10.127.1.1.2.1.1", "docsIfUpChannelId", decode)
    decode = re.sub("1.3.6.1.2.1.10.127.1.1.2.1.2", "docsIfUpChannelFrequency", decode)
    decode = re.sub("1.3.6.1.2.1.10.127.1.1.2.1.3", "docsIfUpChannelWidth", decode)
    decode = re.sub("1.3.6.1.2.1.10.127.1.1.2.1.15", "docsIfUpChannelType", decode)
    decode = re.sub(
        "1.3.6.1.4.1.4115.1.3.4.1.9.2.1.2",
        "arrisCmDoc30IfUpChannelExtendedSymbolRate",
        decode,
    )
    decode = re.sub(
        "1.3.6.1.4.1.4115.1.3.4.1.9.2.1.3",
        "arrisCmDoc30IfUpChannelExtendedModulation",
        decode,
    )
    decode = re.sub(
        "1.3.6.1.4.1.4491.2.1.20.1.2.1.1", "docsIf3CmStatusUsTxPower", decode
    )
    decode = re.sub(
        "1.3.6.1.4.1.4491.2.1.20.1.2.1.2", "docsIf3CmStatusUsT3Timeouts", decode
    )
    decode = re.sub(
        "1.3.6.1.4.1.4491.2.1.20.1.2.1.3", "docsIf3CmStatusUsT4Timeouts", decode
    )
    decode = re.sub(
        "1.3.6.1.4.1.4491.2.1.20.1.24.1.1", "docsIf3SignalQualityExtRxMER", decode
    )
    decode = re.sub("1.3.6.1.2.1.10.127.1.1.4.1.3", "docsIfSigQCorrecteds", decode)
    decode = re.sub("1.3.6.1.2.1.10.127.1.1.4.1.4", "docsIfSigQUncorrectables", decode)
    decode = re.sub("1.3.6.1.2.1.10.127.1.1.4.1.5", "docsIfSigQSignalNoise", decode)
    decode = re.sub("1.3.6.1.2.1.69.1.5.8.1.2", "DevEvFirstTimeOid", decode)
    decode = re.sub("1.3.6.1.2.1.69.1.5.8.1.5", "DevEvId", decode)
    decode = re.sub("1.3.6.1.2.1.69.1.5.8.1.7", "DevEvText", decode)
    decode = re.sub("1.3.6.1.2.1.126.1.1.1.1.1", "docsBpi2CmPrivacyEnable", decode)
    decode = re.sub(
        "1.3.6.1.4.1.4491.2.1.21.1.3.1.8", "docsQosServiceFlowPrimary", decode
    )
    # decode = re.sub("1.3.6.1.2.1.69.1.4.5.0", "docsDevServerConfigFile", decode)

    # parse json
    jresponse = json.loads(decode)

    # filter numeric oid's
    jresponse = {k: jresponse[k] for k in jresponse if re.match("^[a-zA-Z]", k)}

    for key, value in jresponse.items():
        logging.debug("%s: %s" % (key, value))

    # Write to Influxdb
    if influx.lower() == "true":
        logging.info("InfluxDB output is enabled, posting outputs now...")

        from influxdb import InfluxDBClient

        json_body = []
        for key, value in jresponse.items():
            x = key.split(".")
            if value.isnumeric():
                value = int(value)
            json_body.append(
                {
                    "measurement": x[0],
                    "tags": {"channel": x[1]},
                    "time": current_time,
                    "fields": {"value": value},
                }
            )
        logging.debug(json_body)

        if influx_user != "" and influx_password != "":
            client = InfluxDBClient(
                host=influx_server,
                port=influx_port,
                username=influx_user,
                password=influx_password,
            )
        else:
            client = InfluxDBClient(host=influx_server, port=influx_port)

        client.switch_database(influx_database)
        success = client.write_points(json_body, time_precision="ms")
        if not success:
            logging.error("Error writing to influx database")

    # Push to MQTT
    if mqtt.lower() == "true":
        logging.info("MQTT output is enabled, posting results now...")
        import paho.mqtt.publish as publish

        msgs = []
        mqtt_topic = "".join(
            [mqtt_client, "/"]
        )  # Create the topic base using the client_id and serial number
        if mqtt_username != "" and mqtt_password != "":
            auth_settings = {"username": mqtt_username, "password": mqtt_password}
        else:
            auth_settings = None

        msgs.append((mqtt_topic + "current_time", current_time, 0, False))
        for key, value in jresponse():
            msgs.append((mqtt_topic + key, value, 0, False))


def main():
    global next_run_yes
    try:
        do_work()
    except Exception as e:
        logging.error("%s : %s" % (type(e).__name__, str(e)))
    next_run_yes = 1

global next_run_yes

get_loglevel = os.environ["LOG_LEVEL"]
loglevel = logging.INFO
if get_loglevel.lower() == "info":
    loglevel = logging.INFO
elif get_loglevel.lower() == "error":
    loglevel = logging.ERROR
elif get_loglevel.lower() == "debug":
    loglevel = logging.DEBUG

logging.basicConfig(level=loglevel, format="%(asctime)s %(levelname)s %(message)s")
logging.info("Started modem scraper")

schedule.every(5).minutes.do(main).run()
while True:
    if next_run_yes == 1:
        next_run = schedule.next_run().strftime("%d/%m/%Y %H:%M:%S")
        logging.info("Next run is scheduled at %s" % next_run)
        next_run_yes = 0
    schedule.run_pending()
    time.sleep(1)
