import django
from django.conf import settings
from celery import Celery


django.setup()

app = Celery('zeesilver')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {repr(self.request)}')
