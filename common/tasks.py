from django.core import management
from django.contrib.sessions.models import Session
from celery.decorators import periodic_task
from celery.schedules import crontab
from celery.utils.log import get_logger
from cart.cart import Cart


logger = get_logger(__name__)


@periodic_task(run_every=crontab(minute=0, hour='*/6'))
def clearcarts_task():
    management.call_command('clearcarts')


@periodic_task(run_every=crontab(minute=0, hour=0, day_of_month=16))
def update_geoip_task():
    try:
        management.call_command('updategeodb')
    except management.CommandError as e:
        logger.error(e)
