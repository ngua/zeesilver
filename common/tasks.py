from django.core import management
from django.core.mail import mail_admins
from celery.decorators import periodic_task, task
from celery.schedules import crontab
from celery.utils.log import get_logger
from html2text import html2text


logger = get_logger(__name__)


@periodic_task(run_every=crontab(minute=0, hour='*/6'))
def auto_clear_carts():
    management.call_command('clearcarts')


@periodic_task(run_every=crontab(minute=0, hour=0, day_of_month=16))
def update_geoip():
    try:
        management.call_command('updategeodb')
    except management.CommandError as e:
        logger.error(e)


@task(name='notify_admins')
def notify_admins(subject, body, **kwargs):
    plain_text = html2text(body)
    mail_admins(subject, message=plain_text, html_message=body, **kwargs)
