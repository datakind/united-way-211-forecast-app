FROM python:3.9.13-slim-buster

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN apt-get update && pip install --upgrade pip && pip install -r requirements.txt \
&& rm -rf /var/cache/apk/*

COPY . /app

CMD ["python","app.py"]
# We are only doing this for now for the presentation
# Afterwards, gunicorn will be used again after testing.
# Gunicorn seems to work with websockets as long as
# the platform build lines up. If you are using CI with 
# Heroku, this may not be possible, so Gevent MUST be used
# or a thread handler process.