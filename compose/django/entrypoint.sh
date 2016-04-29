#!/bin/sh
set -e
# This entrypoint is used to play nicely with the current cookiecutter configuration.
# Since docker-compose relies heavily on environment variables itself for configuration, we'd have to define multiple
# environment variables just to support cookiecutter out of the box. That makes no sense, so this little entrypoint
# does all this for us.
export REDIS_URL=redis://172.17.42.1:16379/7
export CELERY_BROKER_URL=$REDIS_URL

# the official postgres image uses 'postgres' as default user if not set explictly.
#if [ -z "$POSTGRES_ENV_POSTGRES_USER" ]; then
#    export POSTGRES_ENV_POSTGRES_USER=postgres
#fi

#export DATABASE_URL=postgres://$POSTGRES_ENV_POSTGRES_USER:$POSTGRES_ENV_POSTGRES_PASSWORD@postgres:5432/$POSTGRES_ENV_POSTGRES_USER

#cd /app && git pull

exec "$@"
