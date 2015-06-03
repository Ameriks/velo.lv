from django.utils.translation import ugettext_lazy
from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('PGSQL_DB', 'velolv'),
        'USER': os.environ.get('PGSQL_USER', 'velolv'),
        'PASSWORD': os.environ['PGSQL_PASS'],
        'HOST': '172.17.42.1',
        'PORT': '15005',
    },
    # TEMPORARY disabled while migrating 1.8.2
    # 'legacy': {
    #     'NAME': 'velo',
    #     'ENGINE': 'django.db.backends.mysql',
    #     'USER': 'whazaa',
    #     'PASSWORD': os.environ['LEGACY_MYSQL_PASS'],
    #     'HOST': '91.135.19.3',
    #     'PORT': '3306'
    # },
}

EMAIL_BACKEND = 'django_mailgun.MailgunBackend'

SESSION_COOKIE_DOMAIN = '.velo.lv'
#LANGUAGE_COOKIE_DOMAIN = '.velo.lv'
#CSRF_COOKIE_DOMAIN = '.velo.lv'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '%s:11211' % os.environ.get('MEMCACHE_IP', '127.0.0.1'),
    }
}


# This is here due to issues with website speed in production.
# INTERNAL_IPS = ('87.99.89.245', '172.17.42.1', '87.99.89.245, 172.17.42.1')
# INSTALLED_APPS += ('debug_toolbar', 'django_extensions', 'template_timings_panel', )
# DEBUG_TOOLBAR_CONFIG = {
#     'INTERCEPT_REDIRECTS': False,
# }
# DEBUG_TOOLBAR_PANELS = [
#     'debug_toolbar.panels.versions.VersionsPanel',
#     'debug_toolbar.panels.timer.TimerPanel',
#     'debug_toolbar.panels.settings.SettingsPanel',
#     'debug_toolbar.panels.headers.HeadersPanel',
#     'debug_toolbar.panels.request.RequestPanel',
#     'debug_toolbar.panels.sql.SQLPanel',
#     'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#     'debug_toolbar.panels.templates.TemplatesPanel',
#     'debug_toolbar.panels.cache.CachePanel',
#     'debug_toolbar.panels.signals.SignalsPanel',
#     'debug_toolbar.panels.logging.LoggingPanel',
#     'debug_toolbar.panels.redirects.RedirectsPanel',
#     'template_timings_panel.panels.TemplateTimings.TemplateTimings',
# ]
# MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware', 'velo.middleware.ProfileMiddleware')

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)


ADMIN_URL = os.environ.get('ADMIN_URL', 'administrator')

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SSL_SLAPPER_SSL_REDIRECT_ANONYMOUS=True
SSL_SLAPPER_SSL_REDIRECT_AUTHENTICATED=True
SSL_SLAPPER_LOGIN_PAGE=LOGIN_URL
SSL_SLAPPER_SSL_ONLY_PAGES=("^%s$" % LOGIN_URL,
                            "^%s$" % reverse_lazy('admin:index'),
                            "^%s" % reverse_lazy('application'),
                            "^%s" % reverse_lazy('manager:competition_list'),
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
                            )

RAVEN_CONFIG = {
    'dsn': 'https://d705b5ab401a485fbf0fd2f275984224:{0}@{1}/2'.format(os.environ['RAVEN_KEY'], os.environ['RAVEN_HOST']),
}