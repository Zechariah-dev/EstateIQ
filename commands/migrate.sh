#!/bin/bash
#  Get the environment variable of super user email
SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL:-"dev.codertjay@gmail.com.com"}
SUPERUSER_FIRST_NAME=${DJANGO_SUPERUSER_FIRST_NAME:-"EstateIQ"}
SUPERUSER_LAST_NAME=${DJANGO_SUPERUSER_LAST_NAME:-"EstateIQ"}
#  move to the app location
cd /app/

#  collecstatic with no output shown
/opt/venv/bin/python manage.py collectstatic --noinput

#  migrate the database
/opt/venv/bin/python manage.py migrate --noinput
#  create a super user with the email set
/opt/venv/bin/python manage.py createsuperuser --email $SUPERUSER_EMAIL --first_name $SUPERUSER_FIRST_NAME --last_name $SUPERUSER_LAST_NAME  --noinput  || true