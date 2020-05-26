from celery.decorators import task
from django.core.mail import mail_admins


@task(name='mail_admins_task')
def mail_admins_task(subject, message):
    mail_admins(subject, message)
