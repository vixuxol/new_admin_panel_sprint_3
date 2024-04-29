FROM python:3.10

# working directory
WORKDIR /opt/app

# set environment 
ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'config.settings'

COPY ./src/uwsgi/uwsgi.ini ./uwsgi.ini
COPY ./src/requirements.txt requirements.txt

RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && mkdir -p /opt/app/static/ \
     && mkdir -p /opt/app/media/

RUN apt update \
    && apt install -y gcc libc-dev gettext netcat-traditional

RUN pip install --upgrade pip setuptools wheel \
     && pip install -r requirements.txt

COPY ./src .

EXPOSE 8000

ENTRYPOINT ["/opt/app/entrypoint.sh"]