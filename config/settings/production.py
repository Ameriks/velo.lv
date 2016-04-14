# -*- coding: utf-8 -*-
'''
Production Configurations

- Use djangosecure
- Use Amazon's S3 for storing static files and uploaded media
- Use mailgun to send emails
- Use Redis on Heroku

- Use sentry for error logging

'''
from __future__ import absolute_import, unicode_literals


from boto.s3.connection import OrdinaryCallingFormat
from django.utils import six

import logging


from .common import *  # noqa

# SECRET CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Raises ImproperlyConfigured exception if DJANGO_SECRET_KEY not in os.environ
SECRET_KEY = env("SECRET_KEY")

# This ensures that Django will be able to detect a secure connection
# properly on Heroku.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# django-secure
# ------------------------------------------------------------------------------
# INSTALLED_APPS += ("djangosecure", )
# raven sentry client
# See https://docs.getsentry.com/hosted/clients/python/integrations/django/
# INSTALLED_APPS += ('raven.contrib.django.raven_compat', )
# SECURITY_MIDDLEWARE = (
#     'djangosecure.middleware.SecurityMiddleware',
# )
# RAVEN_MIDDLEWARE = ('raven.contrib.django.raven_compat.middleware.Sentry404CatchMiddleware',
#                     'raven.contrib.django.raven_compat.middleware.SentryResponseErrorIdMiddleware',)
# MIDDLEWARE_CLASSES = SECURITY_MIDDLEWARE + \
#     RAVEN_MIDDLEWARE + MIDDLEWARE_CLASSES


# set this to 60 seconds and then to 518400 when you can prove it works
# SECURE_HSTS_SECONDS = 60
# SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
#     "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
# SECURE_FRAME_DENY = env.bool("DJANGO_SECURE_FRAME_DENY", default=True)
# SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
#     "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True)
# SECURE_BROWSER_XSS_FILTER = True
# SESSION_COOKIE_SECURE = False
# SESSION_COOKIE_HTTPONLY = True
# SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)

# SITE CONFIGURATION
# ------------------------------------------------------------------------------
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.6/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['.velo.lv'])
# END SITE CONFIGURATION

INSTALLED_APPS += ("gunicorn", )

# Static Assets
# ------------------------
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# EMAIL
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL',
                         default='Ameri System <noreply@is.ameri.lv>')
EMAIL_BACKEND = 'django_mailgun.MailgunBackend'
MAILGUN_ACCESS_KEY = env('DJANGO_MAILGUN_API_KEY')
MAILGUN_SERVER_NAME = env('DJANGO_MAILGUN_SERVER_NAME')
EMAIL_SUBJECT_PREFIX = env("DJANGO_EMAIL_SUBJECT_PREFIX", default='[Ameri System] ')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)
# NEW_RELIC_LICENSE_KEY = env('NEW_RELIC_LICENSE_KEY')
# NEW_RELIC_APP_NAME = 'Ameri System'

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See:
# https://docs.djangoproject.com/en/dev/ref/templates/api/#django.template.loaders.cached.Loader
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader', 'django.template.loaders.app_directories.Loader', ]),
]

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
DATABASES['default'] = env.db("DATABASE_URL")

# CACHING
# ------------------------------------------------------------------------------
# Heroku URL does not pass the DB number, so we parse it in
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env.cache_url('REDIS_URL', default="redis://172.17.42.1:16379/7"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,  # mimics memcache behavior.
                                        # http://niwinz.github.io/django-redis/latest/#_memcached_exceptions_behavior
        }
    }
}

BROKER_URL = env("CELERY_BROKER_URL", default="redis://172.17.42.1:16379/7")


# Sentry Configuration
# SENTRY_DSN = env('DJANGO_SENTRY_DSN')
# SENTRY_CLIENT = env('DJANGO_SENTRY_CLIENT', default='raven.contrib.django.raven_compat.DjangoClient')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True
        },
        'django.security.DisallowedHost': {
            'level': 'ERROR',
            'handlers': ['console', 'mail_admins'],
            'propagate': True
        }
    }
}
# SENTRY_CELERY_LOGLEVEL = env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO)
# RAVEN_CONFIG = {
#     'CELERY_LOGLEVEL': env.int('DJANGO_SENTRY_LOG_LEVEL', logging.INFO),
#     'DSN': SENTRY_DSN
# }

# Custom Admin URL, use {% url 'admin:index' %}
ADMIN_URL = env('DJANGO_ADMIN_URL')

# Your production stuff: Below this line define 3rd party library settings
SESSION_COOKIE_DOMAIN = '.velo.lv'

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True



RABBITMQ_USER = 'velolv'
RABBITMQ_PASS = env('RABBITMQ_PASS')
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