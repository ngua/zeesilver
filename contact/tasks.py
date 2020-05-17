from celery.decorators import task
from celery.utils.log import get_task_logger
from django.core.mail import mail_admins


logger = get_task_logger(__name__)


@task(name='mail_admins_task')
def mail_admins_task(subject, message):
    logger.info('Admin contact notification email sent')
    mail_admins(subject, message)
