import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from .base import *


SECRET_KEY = os.environ.get('SECRET_KEY')
FERNET_KEY = bytes(os.environ.get('FERNET_KEY').encode('UTF-8'))
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')
DEBUG = False
MIDDLEWARE += [
    'shop.middleware.ShopAvailableMiddleware',
]

# Logging and sentry

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}

IGNORE_ERRORS = [KeyboardInterrupt]
sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[DjangoIntegration()],
    ignore_errors=IGNORE_ERRORS
)

# Static and media files

DEFAULT_FILE_STORAGE = 'storage.SpacesMediaStorage'
STATICFILES_STORAGE = 'storage.SpacesStaticStorage'
PATH_PREFIX = 'zeesilver'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_LOCATION = f'{PATH_PREFIX}/static'

MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
MEDIAFILES_LOCATION = f'{PATH_PREFIX}/media'

AWS_ACCESS_KEY_ID = os.environ.get('SPACES_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('SPACES_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('SPACES_BUCKET')
AWS_S3_ENDPOINT_URL = os.environ.get('SPACES_ENDPOINT')
AWS_S3_CUSTOM_DOMAIN = os.environ.get('SPACES_EDGE')
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'static'
AWS_DEFAULT_ACL = 'public-read'

# Collectfast

COLLECTFAST_STRATEGY = 'collectfast.strategies.boto3.Boto3Strategy'
COLLECTFAST_CACHE = 'collectfast'
COLLECTFAST_THREADS = 10
