# -*- coding: utf-8 -*-
"""
Django settings for Ameri System project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""
from __future__ import absolute_import, unicode_literals

import environ

ROOT_DIR = environ.Path(__file__) - 3  # (/a/b/myfile.py - 3 = /)
APPS_DIR = ROOT_DIR.path('velo')

env = environ.Env()



# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.admin',
    'django.contrib.gis',
)
THIRD_PARTY_APPS = (
    'crispy_forms',  # Form layouts
    'easy_thumbnails',
    'easy_thumbnails.optimize',
    'sitetree',
    'django_tables2',
    'django_tables2_reports',
    'django_filters',
    'django_select2',

    'mptt',
    'djcelery',
    'ckeditor',
    'impersonate',

    'allauth',  # registration
    'allauth.account',  # registration
    'allauth.socialaccount',  # registration
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.twitter',
    'allauth.socialaccount.providers.draugiem',
    # 'shorturls',  # NOT READY FOR Python 3
)

LOCAL_APPS = (
    'velo.core',
    'velo.payment',
    'velo.team',
    'velo.registration',
    'velo.results',
    'velo.manager',
    'velo.velo',
    'velo.supporter',
    'velo.advert',
    'velo.news',
    'velo.marketing',
    'velo.staticpage',
    'velo.gallery',
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'velo.velo.middleware.SSLRedirectMiddleware', # CUSTOM
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',  # CUSTOM
    'impersonate.middleware.ImpersonateMiddleware',  # CUSTOM
)

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'velo.contrib.sites.migrations'
}


# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("""Agris""", 'velo@pd.lv'),
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    # Raises ImproperlyConfigured exception if DATABASE_URL not in os.environ
    'default': env.db("DATABASE_URL", default="postgis://velolv:velolv@dev.docker.local/velolv"),
}

DATABASES['default']['ATOMIC_REQUESTS'] = True

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Riga'


# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'lv'

LANGUAGES = (
    ('lv', 'Latvian'),
    ('en', 'English'),
)


# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.org/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Some really nice defaults
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'

ACCOUNT_ALLOW_REGISTRATION = env.bool("DJANGO_ACCOUNT_ALLOW_REGISTRATION", True)
ACCOUNT_ADAPTER = 'velo.core.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'velo.core.adapters.SocialAccountAdapter'

ACCOUNT_SIGNUP_FORM_CLASS = 'velo.core.forms.SignupForm'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'core.User'
LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = 'account_login'


# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'


########## CELERY
# INSTALLED_APPS += ('ameri.taskapp.celery.CeleryConfig',)
# if you are not using the django database broker (e.g. rabbitmq, redis, memcached), you can remove the next line.
#INSTALLED_APPS += ('kombu.transport.django',)
#BROKER_URL = env("CELERY_BROKER_URL", default='django://')
########## END CELERY


# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'



HASH_ALPHABET = 'abcdefghjkmnprstuvwxyzABCDEFGHJKMNPRSTUVWXYZ23456789'





CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = '//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'toolbar_Basic': [
            ['Source', '-', 'Bold', 'Italic']
        ],
        'toolbar_full': [
            ['PasteText', 'PasteFromWord', 'RemoveFormat'],
            ['Styles', 'Format', 'Bold', 'Italic', 'Underline', 'Strike', 'SpellChecker', 'Undo', 'Redo'],
            ['JustifyLeft', 'JustifyCenter', 'JustifyRight'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink', 'Anchor'],
            ['Image', 'Flash', 'Table', 'HorizontalRule'],
            ['TextColor', 'BGColor'],
            ['SpecialChar', 'Iframe'], ['Source'],
        ],
    },
}

SECRET_KEY = env("SECRET_KEY")
SECRET_KEY2 = env('SECRET_KEY2')  # For short URLS
LEGACY_KEY = env('LEGACY_KEY')  # TODO: Remove this variable

VIMEO_KEY = env('VIMEO_KEY')
VIMEO_SECRET = env('VIMEO_SECRET')
VIMEO_TOKEN = env('VIMEO_TOKEN')


AUTO_RENDER_SELECT2_STATICS = False

SMS_USERNAME = env('SMS_USERNAME')
SMS_PASSWORD = env('SMS_PASSWORD')
SMS_GATEWAY = 'https://smsmarketing.bpo.lv'

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

SERVER_EMAIL = "webmaster@mans.velo.lv"

MAILGUN_FROM = u'Tavs velo.lv <hi@mans.velo.lv>'
MAILGUN_ACCESS_KEY = env('MAILGUN_ACCESS_KEY')
MAILGUN_URL = 'https://api.mailgun.net/v2'
MAILGUN_SERVER_NAME = 'mans.velo.lv'


MY_DEFAULT_DOMAIN = 'https://mans.velo.lv'
SHORT_BASE_URL = 'http://mans.velo.lv/s/'

REPLACE_AUTH_USER_ADMIN = False

USER_FIELDS = ['email', ]
PROTECTED_USER_FIELDS = ['email', ]

EREKINS_IJSA_DEFAULT_VAT = "/api/v1/vat/18/"
EREKINS_LKDF_DEFAULT_VAT = "/api/v1/vat/16/"
EREKINS_IJSA_DEFAULT_LANGUAGE = "/api/v1/language/10/"
EREKINS_LKDF_DEFAULT_LANGUAGE = "/api/v1/language/9/"
EREKINS_IJSA_DEFAULT_CREATOR = "/api/v1/employee/9/"
EREKINS_LKDF_DEFAULT_CREATOR = "/api/v1/employee/5/"

FIRST_DAY_OF_WEEK = 1

IMPERSONATE_REQUIRE_SUPERUSER = True

THUMBNAIL_ALIASES = {
    'supporter': {
        'agencysupporter': {'size': (240, 180), 'crop': False},
    },
    'gallery': {
        'thumb': {'size': (300, 300), 'crop': True},
        'img': {'size': (1000, 1000), 'crop': False},
        'news_thumb': {'size': (400, 250), 'crop': True},
        'news': {'size': (850, 300), 'crop': True},
    },
    'core': {
        'email_logo': {'size': (210, 120), 'crop': False},
        'email_logo_double': {'size': (420, 240), 'crop': False},
    },
    'news': {

    }
}

THUMBNAIL_OPTIMIZE_COMMAND = {
    'png': '/usr/bin/optipng {filename}',
    'gif': '/usr/bin/optipng {filename}',
    'jpeg': '/usr/bin/jpegoptim --strip-all {filename}'
}
THUMBNAIL_BASEDIR = 'easy_thumbnails'
THUMBNAIL_CHECK_CACHE_MISS = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
USE_X_FORWARDED_HOST = True

ALWAYS_SSL_PAGES = []

SHORTEN_MODELS = {
    'n': 'news.news',
}
