FROM python:3.9.13-slim-buster

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install git -y && pip install --upgrade pip && pip install -r requirements.txt \
&& rm -rf /var/cache/apk/*

COPY . /app

CMD ["python","starter/start.py"]