#!/bin/sh
set -e


export REDIS_URL=redis://172.17.42.1:16379/7
export CELERY_BROKER_URL=$REDIS_URL

python /app/manage.py collectstatic --noinput



exec "$@"
