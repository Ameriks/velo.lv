from django.utils.translation import ugettext_lazy
from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('PGSQL_DB', 'velolv'),
        'USER': os.environ.get('PGSQL_USER', 'velolv'),
        'PASSWORD': os.environ['PGSQL_PASS'],
        'HOST': '192.168.110.128',
        'PORT': 6432,
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

ADMIN_URL = os.environ['ADMIN_URL']

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
                            "^/lv/maksajums",
                            "^/lv/konts",
                            "^/en/application",
                            "^/en/payment",
                            "^/en/accounts",
                            )