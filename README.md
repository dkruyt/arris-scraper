# arris-scraper
[![Docker](https://github.com/dkruyt/arris-scraper/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/dkruyt/arris-scraper/actions/workflows/docker-publish.yml)

Scrapes satistics from a Arris modem and outputs it to influxdb or mqtt.

You can also move the environment variables into an ENV file and invoke that on the commandline when invoking the docker image.
## Configuration
### Environment variables

| Environment variable      | Required | Description                                                                                          | Default value   |
|---------------------------|----------|------------------------------------------------------------------------------------------------------|-----------------|
| LOG_LEVEL                 | No       | Logging level (ERROR, INFO, DEBUG)                                                                   | `INFO`          |
| USE_INFLUX                | No       | Set to true if you want to use InfluxDB as output                                                    | `false`         |
| INFLUX_DATABASE           | No       | InfluxDB DB name                                                                                     | `influxdb`      |
| INFLUX_SERVER             | No       | InfluxDB server                                                                                      | `localhost`     |
| INFLUX_PORT               | No       | InfluxDB server port                                                                                 | `8086`          |
| INFLUX_USER               | No       | InfluxDB User                                                                                        | *empty*         |
| INFLUX_PASSWORD           | No       | InfluxDB Password                                                                                    | *empty*         |
| USE_MQTT                  | No       | Set to true if you want to use MQTT as output                                                        | `false`         |
| MQTT_CLIENT_ID            | No       | MQTT client ID                                                                                       | `pv`            |
| MQTT_SERVER               | No       | MQTT server                                                                                          | `localhost`     |
| MQTT_USERNAME             | No       | MQTT username                                                                                        | *empty*         |
| MQTT_PASSWORD             | No       | MQTT password                                                                                        | *empty*         |

# Grafana

![grafana](https://github.com/dkruyt/arris-scraper/blob/main/images/grafana.png)
