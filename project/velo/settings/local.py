# This is required for docker dev environment to setup variables in SSH connection.

import re, os
from velo.utils import listdir

for envfile in listdir("/etc/container_environment"):
    name = os.path.basename(envfile)
    with open("/etc/container_environment/" + envfile, "r") as f:
        value = re.sub('\n\Z', '', f.read())
    os.environ[name] = value

from .base import *

DEBUG = True
TEMPLATE_DEBUG=True
THUMBNAIL_DEBUG = True

INSTALLED_APPS += (
    'rosetta',
)

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/var/log/emails'


INSTALLED_APPS += ('debug_toolbar', 'django_extensions', )
INTERNAL_IPS = ('127.0.0.1', '192.168.56.1', )

MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', )


DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}


TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'


CACHES = {
    'default': {
        #'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '/var/tmp/django_cache',
    },
}

ALLOWED_HOSTS = ['tst.velo.lv:8000', ]


#LOGGING.get('loggers', {}).get('django.db.backends', {}).update({'level': 'DEBUG'})


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'velolv',
        'USER': 'velolv',
        'PASSWORD': os.environ['PGSQL_PASS'],
        'HOST': '192.168.56.100',
    },
    # 'legacy': {
    #     'NAME': 'velo',
    #     'ENGINE': 'django.db.backends.mysql',
    #     'USER': 'root',
    #     'PASSWORD': '1234567890',
    #     'HOST': '192.168.56.1',
    #     'PORT': '13306'
    # }
}
