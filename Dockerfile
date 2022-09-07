FROM --platform=linux/arm64/v8 python:3.9.13-slim-buster

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN apt-get update && pip install --upgrade pip && pip install -r requirements.txt \
&& rm -rf /var/cache/apk/*

COPY . /app

CMD ["gunicorn", "wsgi:app", "--bind=0.0.0.0:5000"]

# export DOCKER_DEFAULT_PLATFORM=linux/amd64