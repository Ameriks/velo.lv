
from __future__ import absolute_import
import os
from celery import Celery
from django.apps import AppConfig
from django.conf import settings


if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")  # pragma: no cover


app = Celery('velo')


class CeleryConfig(AppConfig):
    name = 'velo.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        # Using a string here means the worker will not have to
        # pickle the object when using Windows.
        app.config_from_object('django.conf:settings')
        app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)

        if hasattr(settings, 'RAVEN_CONFIG'):
            # Celery signal registration
            from raven import Client
            from raven.contrib.celery import register_signal
            client = Client(dsn=settings.RAVEN_CONFIG['DSN'])
            register_signal(client)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))  # pragma: no cover
