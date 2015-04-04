from .base import *

DEBUG = True
TEMPLATE_DEBUG=True
THUMBNAIL_DEBUG = True

INSTALLED_APPS += (
    'rosetta',
)

EMAIL_HOST = '192.168.59.3'
EMAIL_PORT = 1025


INSTALLED_APPS += ('debug_toolbar', 'django_extensions', 'template_timings_panel', )
INTERNAL_IPS = ('87.99.89.245', '87.99.89.245, 172.17.42.1', '192.168.59.3')

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
    'template_timings_panel.panels.TemplateTimings.TemplateTimings',
]

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}


CACHES = {
    'default': {
        #'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '/var/tmp/django_cache',
    },
}

ALLOWED_HOSTS = ['docker.local:58000', 'docker.local',]


LOGGING.get('loggers', {}).get('django.db.backends', {}).update({'level': 'DEBUG'})

MY_DEFAULT_DOMAIN = 'http://docker.local:58000'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'velolv',
        'USER': 'velolv',
        'PASSWORD': os.environ['PGSQL_PASS'],
        'HOST': '192.168.59.103',
    },
    'legacy': {
        'NAME': 'velo',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'whazaa',
        'PASSWORD': os.environ['LEGACY_MYSQL_PASS'],
        'HOST': '91.135.19.3',
        'PORT': '3306'
    },
}
