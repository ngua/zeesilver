from django.core import management
from django.contrib.sessions.models import Session
from celery.decorators import periodic_task
from celery.schedules import crontab
from cart.cart import Cart


@periodic_task(run_every=crontab(minute=0, hour='*/6'))
def clearcarts_task():
    management.call_command('clearcarts')
