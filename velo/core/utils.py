import logging

from velo.core.models import Log
from subprocess import call

logger = logging.getLogger('velo.core')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_message(action, message='', params='{}', user=None, object=None):
    try:
        log = Log(action=action, message=message, params=params)
        if user:
            log.user = user
        if object:
            log.content_object = object
        log.save()
        return log
    except:
        logger.exception("Exception writing logs")


def restart_celerybeat():
    call(["s6-svc", "-h", "/var/run/s6/services/celerybeat"])
