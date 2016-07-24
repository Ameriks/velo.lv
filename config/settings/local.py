# -*- coding: utf-8 -*-
'''
Local settings

- Run in Debug mode
- Use console backend for emails
- Add Django Debug Toolbar
- Add django-extensions as app
'''

from .common import *  # noqa

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DJANGO_DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
THUMBNAIL_DEBUG = True

SECRET_KEY = env("DJANGO_SECRET_KEY", default='CHANGEME!!!7z0c)k$qd19(@)@_qmg(dgxnmsr!dd&f8^s&2_avzww+u)s0x)')


# Mail settings
# ------------------------------------------------------------------------------
EMAIL_HOST = 'host'
EMAIL_PORT = 1025
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
                    default='django.core.mail.backends.smtp.EmailBackend')


# CACHING
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# django-debug-toolbar
# ------------------------------------------------------------------------------
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INSTALLED_APPS += ('debug_toolbar', )

INTERNAL_IPS = ('127.0.0.1', '172.17.0.1',)

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}

# django-extensions
# ------------------------------------------------------------------------------
INSTALLED_APPS += ('django_extensions', )
#
# TESTING
# ------------------------------------------------------------------------------
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Your local stuff: Below this line define 3rd party library settings


INSTALLED_APPS += (
    'rosetta',
)

CELERY_ALWAYS_EAGER = True


MY_DEFAULT_DOMAIN = 'http://dev.docker.local:48000'
SHORT_BASE_URL = 'http://dev.docker.local:48000/s/'

SITETREE_RAISE_ITEMS_ERRORS_ON_DEBUG = False
