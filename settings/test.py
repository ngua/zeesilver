from .base import *


SECRET_KEY = 'nmns&#da1#j)@fdd4fgskjmpbeqfpg9)5^4f-kh+lx%pylm4v5'
FERNET_KEY = b'gHIka0SFIBYAEvR0CgHNI3YJ5CntMROnpU3bRFe9A3Y='
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', 'testserver']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEBUG = True
MIDDLEWARE += ['common.middleware.GeoIPMiddleware']
GEO_WHITELIST = ('US',)

# celery settings
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'
