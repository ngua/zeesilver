from .base import *

SECRET_KEY = 'nmns&#da1#j)@fdd4fgskjmpbeqfpg9)5^4f-kh+lx%pylm4v5'
DEBUG = True
ALLOWED_HOSTS = ['*']

# Debug toolbar settings
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']


def show_toolbar(request):
    return True


DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": show_toolbar
}
