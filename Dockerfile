FROM python:alpine

ARG VERSION
ARG BUILD_DATE
ARG VCS_REF

LABEL maintainer="dkruyt" \
  org.opencontainers.image.created=$BUILD_DATE \
  org.opencontainers.image.url="https://github.com/dkruyt/arris-scraper" \
  org.opencontainers.image.source="https://github.com/dkruyt/arris-scraper" \
  org.opencontainers.image.version=$VERSION \
  org.opencontainers.image.revision=$VCS_REF \
  org.opencontainers.image.vendor="dkruyt" \
  org.opencontainers.image.title="arris-scraper" \
  org.opencontainers.image.description="Scrapes Arris moden statistics and outputs it to influxdb, mqtt" \
  org.opencontainers.image.licenses="GPL-3.0"

ENV LOG_LEVEL="INFO"

ENV MODEM_URL="https://192.168.100.1/getRouterStatus"

ENV USE_INFLUX="false"
ENV INFLUX_DATABASE="influxdb"
ENV INFLUX_SERVER="localhost"
ENV INFLUX_PORT="8086"
ENV INFLUX_PASSWORD=""
ENV INFLUX_USER=""

ENV USE_MQTT="false"
ENV MQTT_CLIENT_ID="pv"
ENV MQTT_SERVER="localhost"
ENV MQTT_USERNAME=""
ENV MQTT_PASSWORD=""

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache --no-cache-dir -r requirements.txt

COPY  scrape-arris.py ./

CMD [ "python", "./scrape-arris.py" ]
