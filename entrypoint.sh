#!/bin/bash

source /app/wait-for-db.sh

export PYTHONPATH=$(pwd)
# python manage.py flush --no-input --settings=$DJANGO_SETTINGS_MODULE
# python manage.py makemigrations --no-input --settings=$DJANGO_SETTINGS_MODULE
# python manage.py migrate --settings=$DJANGO_SETTINGS_MODULE
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); \
#     User.objects.create_superuser($SU_USERNAME, $SU_EMAIL, $SU_PASSWORD)" | python manage.py shell --settings=$DJANGO_SETTINGS_MODULE

exec "$@"
