FROM python:3.9.13-slim-buster

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV OTEL_SERVICE_NAME="uw211forecast"
ENV SPLUNK_ACCESS_TOKEN=<SPLUNK_A_T>
ENV OTEL_TRACES_EXPORTER="jaeger-thrift-splunk"
ENV OTEL_EXPORTER_JAEGER_ENDPOINT="https://ingest.us1.signalfx.com/v2/trace"
ENV OTEL_RESOURCE_ATTRIBUTES='deployment.environment=production'

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install git -y && pip install --upgrade pip && pip install -r requirements.txt \
&& rm -rf /var/cache/apk/*

RUN splunk-py-trace-bootstrap

COPY . /app

CMD splunk-py-trace gunicorn -k eventlet -w 1 app:app -b 0.0.0.0:$PORT