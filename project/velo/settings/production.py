from django.utils.translation import ugettext_lazy
import re
from .base import *

AWS_SES_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SES_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
#AWS_SES_REGION_NAME = 'eu-west-1'
AWS_SES_REGION_ENDPOINT = 'email.eu-west-1.amazonaws.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('PGSQL_DB', 'velolv'),
        'USER': os.environ.get('PGSQL_USER', 'velolv'),
        'PASSWORD': os.environ['PGSQL_PASS'],
        'HOST': '172.17.42.1',
        'PORT': '15005',
    },
    'legacy': {
        'NAME': 'velo',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'whazaa',
        'PASSWORD': os.getenv('LEGACY_MYSQL_PASS'),
        'HOST': '91.135.19.3',
        'PORT': '3306'
    },
}

EMAIL_BACKEND = 'django_ses.SESBackend'

SESSION_COOKIE_DOMAIN = '.velo.lv'
#LANGUAGE_COOKIE_DOMAIN = '.velo.lv'
#CSRF_COOKIE_DOMAIN = '.velo.lv'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '%s:11211' % os.environ.get('MEMCACHE_IP', '127.0.0.1'),
    }
}

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True


#RAVEN_CONFIG = {
#    'dsn': 'https://d705b5ab401a485fbf0fd2f275984224:{0}@{1}/2'.format(os.getenv('RAVEN_KEY'), os.getenv('RAVEN_HOST')),
#}



RABBITMQ_USER = 'velolv'
RABBITMQ_PASS = os.getenv('RABBITMQ_PASS')
RABBITMQ_HOST = '172.17.42.1'
RABBITMQ_PORT = '15015'
RABBITMQ_VHOST = RABBITMQ_USER
BROKER_URL = 'amqp://{user}:{password}@{host}:{port}/{vhost}'.format(user=RABBITMQ_USER, password=RABBITMQ_PASS,
                                                                     host=RABBITMQ_HOST, port=RABBITMQ_PORT,
                                                                     vhost=RABBITMQ_VHOST)

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