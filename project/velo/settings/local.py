from .base import *

DEBUG = True
TEMPLATE_DEBUG=True
THUMBNAIL_DEBUG = True

INSTALLED_APPS += (
    'rosetta',
)

EMAIL_HOST = '192.168.58.1'
EMAIL_PORT = 1025

CELERY_ALWAYS_EAGER = True

INSTALLED_APPS += ('debug_toolbar', 'django_extensions', 'template_timings_panel', )
# INTERNAL_IPS = ('192.168.58.2', )

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


# LOGGING.get('loggers', {}).get('django.db.backends', {}).update({'level': 'DEBUG'})

MY_DEFAULT_DOMAIN = 'http://192.168.58.128:58000'
SHORT_BASE_URL = 'http://192.168.58.128:58000/s/'
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'velolv',
        'USER': 'velolv',
        'PASSWORD': os.getenv('PGSQL_PASS'),
        'HOST': '192.168.58.128',
    },
    'legacy': {
        'NAME': 'velo',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'whazaa',
        'PASSWORD': os.environ['LEGACY_MYSQL_PASS'],
        'HOST': '91.135.19.3',
        'PORT': '3306'
    },
    # 'legacy': {
    #     'NAME': 'velo',
    #     'ENGINE': 'django.db.backends.mysql',
    #     'USER': 'root',
    #     'PASSWORD': 'naigiN8I',
    #     'HOST': '192.168.58.128',
    #     'PORT': '3306'
    # },
}


ALWAYS_SSL_PAGES = [
            "^%s" % ADMIN_URL,
            "^/manager",
            "^/admin",
            ".*\.json$",
            "^/lv/pieteikums",
            "^/lv/uznemuma_pieteikums",
            "^/lv/maksajums",
            "^/lv/konts",
            "^/en/application",
            "^/en/company_application",
            "^/en/payment",
            "^/en/accounts",
            ]