from unipath import Path
import os
import djcelery

PROJECT_ROOT = Path(__file__).ancestor(3)

MEDIA_ROOT = PROJECT_ROOT.child('media')
STATIC_ROOT = PROJECT_ROOT.child('static')
VELO_DIR = os.path.join(PROJECT_ROOT, 'velo')

STATICFILES_DIRS = (
    os.path.join(VELO_DIR, 'static'),
)
TEMPLATE_DIRS = (
    os.path.join(VELO_DIR, 'templates'),
)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Agris', 'velo@pd.lv'),
)
MANAGERS = ADMINS

SERVER_EMAIL = "webmaster@mans.velo.lv"

SECRET_KEY = os.getenv('SECRET_KEY')
SECRET_KEY2 = os.getenv('SECRET_KEY2')
HASH_ALPHABET = 'abcdefghjkmnprstuvwxyzABCDEFGHJKMNPRSTUVWXYZ23456789'

LEGACY_KEY = os.getenv('LEGACY_KEY')

AUTH_USER_MODEL = 'core.User'

ALLOWED_HOSTS = ['.velo.lv', ]

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # For wiki
    'social.apps.django_app.default',
    'raven.contrib.django.raven_compat',
    'mptt',
    'django_tables2',
    'django_tables2_reports',
    'django_select2',
    'crispy_forms',
    'djcelery',
    'sitetree',
    'easy_thumbnails',
    'easy_thumbnails.optimize',
    'redactor',
    'impersonate',
    'core',
    'payment',
    'team',
    'registration',
    'results',
    'manager',
    'velo',
    'supporter',
    'advert',
    'news',
    'marketing',
    'staticpage',
    'gallery',
   # 'legacy',
)

VIMEO_KEY = os.getenv('VIMEO_KEY')
VIMEO_SECRET = os.getenv('VIMEO_SECRET')
VIMEO_TOKEN = os.getenv('VIMEO_TOKEN')


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'velo.middleware.JoomlaSessionMiddleware',
    'velo.middleware.IPMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social.apps.django_app.middleware.SocialAuthExceptionMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
)

ROOT_URLCONF = 'velo.urls'

WSGI_APPLICATION = 'velo.wsgi.application'

#DATABASE_ROUTERS = ['legacy.router.LegacyRouter']


LANGUAGE_CODE = 'lv'
gettext = lambda s: s
LANGUAGES = (
    ('lv', gettext('Latvian')),
    ('en', gettext('English')),
)

SITE_ID = 1

TIME_ZONE = 'Europe/Riga'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
MEDIA_URL = '/media/'

from django.core.urlresolvers import reverse_lazy
LOGIN_URL = reverse_lazy('accounts:login')
LOGIN_REDIRECT_URL = reverse_lazy('accounts:profile')

ENFORCED_PASSWORD_CHANGE_VIEW_NAME = 'accounts:password_change'
LOGIN_VIEW_NAME = 'accounts:login'
LOGOUT_VIEW_NAME = 'accounts:logout'

SOCIAL_AUTH_FACEBOOK_KEY = '175838825855542'
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

SOCIAL_AUTH_TWITTER_KEY = 'KOd36nFdR0LSCQCm9EqOBQ'
SOCIAL_AUTH_TWITTER_SECRET = os.getenv('SOCIAL_AUTH_TWITTER_SECRET')

SOCIAL_AUTH_DRAUGIEM_APP_ID = '15007685'
SOCIAL_AUTH_DRAUGIEM_KEY = os.getenv('SOCIAL_AUTH_DRAUGIEM_KEY')

SOCIAL_AUTH_USER_MODEL = 'core.User'
SOCIAL_AUTH_FORCE_EMAIL_VALIDATION = True

SOCIAL_AUTH_LOGIN_ERROR_URL = reverse_lazy('accounts:login')

SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'velo.draugiem.DraugiemPassportAPI',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    'django.core.context_processors.request',
    "django.contrib.messages.context_processors.messages",
    "social.apps.django_app.context_processors.backends",
    "social.apps.django_app.context_processors.login_redirect",
)

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
    'velo.hashers.MD5CustomPasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'

AUTO_RENDER_SELECT2_STATICS = False

SMS_USERNAME = os.getenv('SMS_USERNAME')
SMS_PASSWORD = os.getenv('SMS_PASSWORD')
SMS_GATEWAY = 'http://smsmarketing.bpo.lv'

ADMIN_HONEYPOT_EMAIL_ADMINS = False

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)


CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


MAILGUN_FROM = u'Tavs velo.lv <hi@mans.velo.lv>'
MAILGUN_ACCESS_KEY = os.getenv('MAILGUN_ACCESS_KEY')
MAILGUN_URL = 'https://api.mailgun.net/v2'
MAILGUN_SERVER_NAME = 'mans.velo.lv'


MY_DEFAULT_DOMAIN = 'http://mans.velo.lv'


REPLACE_AUTH_USER_ADMIN = False

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.partial.save_status_to_session',
    'core.pipeline.require_email',
    # 'social.pipeline.mail.mail_validation',
    # 'social.pipeline.social_auth.associate_by_email',
    'core.pipeline.create_user',
    # 'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',

)

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
    },
    'core': {
        'email_logo': {'size': (210, 120), 'crop': False},
        'email_logo_double': {'size': (420, 240), 'crop': False},
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


ADMIN_URL = 'administrator'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
       'simple': {
           'format': '%(levelname)s %(message)s',
       },
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
           'level': 'DEBUG',  # DEBUG
           'class': 'logging.StreamHandler',
           'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.db.backends': {
           'handlers': ['console'],
           'level': 'ERROR',
       },
        'marketing': {
            'level': 'DEBUG',
            'handlers': ['file'],
            'propagate': False,
        },
    }
}
