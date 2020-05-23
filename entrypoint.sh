#!/bin/bash

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 1
    done

    echo "Postgres started"
fi

export PYTHONPATH=$(pwd)
python manage.py flush --no-input --settings=$DJANGO_SETTINGS_MODULE
python manage.py makemigrations --no-input --settings=$DJANGO_SETTINGS_MODULE
python manage.py migrate --settings=$DJANGO_SETTINGS_MODULE
echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
    User.objects.create_superuser($SU_USERNAME, $SU_EMAIL, $SU_PASSWORD)" | python manage.py shell --settings=$DJANGO_SETTINGS_MODULE
python manage.py loaddata listings/fixtures/listings.yaml --settings=$DJANGO_SETTINGS_MODULE
python manage.py loaddata common/fixtures/common.yaml --settings=$DJANGO_SETTINGS_MODULE

exec "$@"
