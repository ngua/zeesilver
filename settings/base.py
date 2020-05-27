"""
Django settings for zeesilver project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import moneyed
from django.contrib.messages import constants as message_constants
from moneyed.localization import _FORMATTER

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'djmoney',
    'ckeditor',
    'django_bleach',
    'crispy_forms',
    'honeypot',
    'solo',
    'localflavor',
    'common',
    'search',
    'cart',
    'merchant',
    'contact',
    'listings',
    'shop'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'cart.middleware.CartTimeoutMiddleware',
    'common.middleware.GeoIPMiddleware'
]

ROOT_URLCONF = 'zeesilver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'common.context_processors.price_points',
                'common.context_processors.in_stock',
                'search.context_processors.search_form',
                'cart.context_processors.cart',
            ],
        },
    },
]

WSGI_APPLICATION = 'zeesilver.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE'),
        'USER': os.environ.get('SQL_USER'),
        'PASSWORD': os.environ.get('SQL_PASSWORD'),
        'NAME': os.environ.get('SQL_DATABASE'),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SQL_PORT', '5432'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'common.User'


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
LISTING_MEDIA = 'listings'

# Messages settings

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'danger'
}

# Redis for caching, celery taskbroker
REDIS_URI = os.environ.get('REDIS_URI')

# Cache

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URI,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Session settings

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'


# Celery settings

CELERY_BROKER_URL = REDIS_URI
CELERY_RESULT_BACKEND = REDIS_URI
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Ckeditor settings

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'custom',
        'toolbar_custom': [
            ['Styles', 'Format', 'Font', 'FontSize'],
            [
                'Bold', 'Italic', 'Underline', 'Strike', 'Subscript',
                'Superscript'
            ],
            ['HorizontalRule', 'Table', '-', 'Link', 'Unlink'],
            ['TextColor', 'BGColor'],
            [
                'NumberedList', 'BulletedList', '-', 'Outdent', 'Indent',
                'Blockquote', '-', 'JustifyLeft', 'JustifyCenter',
                'JustifyRight', 'JustifyBlock'
            ],
            ['Undo', 'Redo'],
            ['RemoveFormat', 'Source'],
        ]
    }
}

# Bleach settings

BLEACH_ALLOWED_TAGS = [
    'p', 'h1', 'h2', 'h3', 'h4', 'em', 'strong', 'a', 'ul', 'ol', 'li', 'br',
    'hr', 'span', 's', 'u', 'table', 'thead', 'tbody', 'tr', 'td',
    'blockquote', 'a'
]
BLEACH_ALLOWED_ATTRIBUTES = [
    'href', 'title', 'name', 'style', 'border', 'cellpadding', 'cellspacing'
]
BLEACH_ALLOWED_STYLES = [
    'font-family', 'font-weight', 'font-size', 'text-decoration',
    'font-variant', 'color', 'width', 'text-align', 'margin-left'
]
BLEACH_STRIP_TAGS = True
BLEACH_DEFAULT_WIDGET = 'ckeditor.widgets.CKEditorWidget'

# Django-money
CURRENCIES = ('USD',)
BASE_CURRENCY = 'USD'
_FORMATTER.add_sign_definition('default', moneyed.USD, prefix='$', suffix='')

# Crispy forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Honeypot
HONEYPOT_FIELD_NAME = 'phonenumber'

# Geoip settings

GEOIP_PATH = os.environ.get('GEOIP_PATH')
GEOIP_COUNTRY = os.environ.get('GEOIP_COUNTRY')
GEOIP_CITY = os.environ.get('GEOIP_CITY')

GEODB_DOMAIN = os.environ.get('GEODB_DOMAIN')
GEODB_COUNTRY = os.environ.get('GEODB_COUNTRY')
GEODB_CITY = os.environ.get('GEODB_CITY')
GEODB_COUNTRY_PERMALINK = f'{GEODB_DOMAIN}/{GEODB_COUNTRY}'
GEODB_CITY_PERMALINK = f'{GEODB_DOMAIN}/{GEODB_CITY}'

# Geolocation restriction settings

GEO_RESTRICTED_VIEWS = ('cart.views', 'shop.views')
GEO_WHITELIST = ('US',)
GEO_KEY = 'GEOIP'

# Session cart settings

CART_KEY = 'CART'
# Expiry time, in seconds, before cart items are removed and returned to stock
CART_TIMEOUT = 3600
CART_TIMEOUT_KEY = 'CART_TIMEOUT'

# ipware settings
PROXY_TRUSTED_IPS = os.environ.get('PROXY_TRUSTED_IPS').split(',')
PROXY_COUNT = int(os.environ.get('PROXY_COUNT'))

# Square Payment settings
SQUARE_APPLICATION_ID = os.environ.get('SQUARE_APPLICATION_ID')
SQUARE_APPLICATION_SECRET = os.environ.get('SQUARE_APPLICATION_SECRET')
SQUARE_ACCESS_TOKEN = os.environ.get('SQUARE_ACCESS_TOKEN')
SQUARE_ENVIRONMENT = os.environ.get('SQUARE_ENVIRONMENT')
SQUARE_DOMAIN = os.environ.get('SQUARE_DOMAIN')
SQUARE_AUTH_URL = os.environ.get('SQUARE_AUTH_URL')

# Order settings
ORDER_KEY = 'ORDER'
