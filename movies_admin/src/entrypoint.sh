#!/bin/sh
set -e

chown www-data:www-data /var/log

if [ "$DATABASE" = "postgres" ]
then
    echo "DB not yet run..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "DB did run."
fi

python manage.py migrate
python manage.py collectstatic --no-input --clear
python manage.py compilemessages
python manage.py createsuperuser --noinput || true

uwsgi --strict --ini /opt/app/uwsgi.ini