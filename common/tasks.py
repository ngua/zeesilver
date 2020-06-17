from django.core import management
from django.contrib.sitemaps import ping_google
from django.core.mail import mail_admins
from celery.decorators import periodic_task, task
from celery.schedules import crontab
from celery.utils.log import get_logger
from html2text import html2text


logger = get_logger(__name__)


@periodic_task(run_every=crontab(minute=0, hour='*/6'))
def auto_clear_carts():
    """
    Clears abandonded carts and return items to inventory, calling
    custom management command defined in common.management
    """
    management.call_command('clearcarts')


@periodic_task(run_every=crontab(minute=0, hour=0, day_of_month=16))
def update_geoip():
    """
    Updates maxmind GeoIP datbases, once a month, using custom management
    command defined in common.management
    """
    try:
        management.call_command('updategeodb')
    except management.CommandError as e:
        logger.error(e)


@task(name='notify_admins')
def notify_admins(subject, body, **kwargs):
    """
    Sends notification email to admins with HTML as attachment
    """
    plain_text = html2text(body)
    mail_admins(subject, message=plain_text, html_message=body, **kwargs)


@periodic_task(run_every=crontab(minute=0, hour=0, day_of_month=1))
def ping():
    """
    Pings google to reindex site once a month
    """
    try:
        ping_google()
    # Exception types vary greatly, need to use bare `except`
    except Exception:
        pass
