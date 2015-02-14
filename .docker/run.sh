#!/bin/bash

set -ex

APP_COMPONENTS="$*"
CELERY_WORKERS=${CELERY_WORKERS:-4}
EXTRA_CMD=${EXTRA_CMD:-}
EXTRA_REQUIREMENTS=${EXTRA_REQUIREMENTS:-}

SUPERVISOR_CONF=/etc/supervisor/conf.d/app.conf

echo "App Components: ${APP_COMPONENTS}"

cd /app
git pull

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep app`" ] ; then
    cat << EOF >> $SUPERVISOR_CONF
[program:app]
priority=10
directory=/app/project
command=/usr/local/bin/uwsgi
    --socket :8080
    -p 4
    -b 32768
    -T
    --master
    --max-requests 5000
    --module velo.wsgi:application
    --touch-reload=velo/wsgi.py

user=root
autostart=true
autorestart=true
stopsignal=QUIT
stdout_events_enabled = true
stderr_events_enabled = true

EOF

fi

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep memcached`" ] ; then
    cat << EOF >> $SUPERVISOR_CONF
[program:memcached]
command=memcached -m 512 -u nobody -l 0.0.0.0
autostart=true
autorestart=true
user=root
priority=5
stdout_events_enabled = true
stderr_events_enabled = true

EOF
fi

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep master-worker`" ] ; then
touch /var/log/celeryworker.log
chown nginx /var/log/celeryworker.log
    cat << EOF >> $SUPERVISOR_CONF
[program:master-worker]
priority=99
directory=/app/project
command=python manage.py celery worker -B -E -c ${CELERY_WORKERS} --autoreload
user=root
autostart=true
autorestart=true
stdout_events_enabled = true
stderr_events_enabled = true

EOF
fi

if [ ! -z "`echo $APP_COMPONENTS | grep "^worker"`" ] ; then
touch /var/log/celeryworker.log
chown nginx /var/log/celeryworker.log
    cat << EOF >> $SUPERVISOR_CONF
[program:worker]
priority=99
directory=/app/project
command=python manage.py celery worker -E -c ${CELERY_WORKERS} --autoreload
user=root
autostart=true
autorestart=true
stdout_events_enabled = true
stderr_events_enabled = true

EOF
fi

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep duplicity`" ] ; then

 if ! grep -q duplicity "/etc/crontab"; then
   echo "5 5 * * * root duplicity --encrypt-key ${BACKUP_BUCKET_ENC_KEY} --exclude /mnt/velo_media/gallery --exclude /mnt/velo_media/easy_thumbnails --archive-dir /app/.duplicity/ --full-if-older-than 30D "/mnt/velo_media" ${BACKUP_BUCKET}" >> /etc/crontab
 fi
    cat << EOF >> $SUPERVISOR_CONF
[program:cron]
command = cron -f -L 15
startsecs = 5
stopwaitsecs = 3600
stopasgroup = false
killasgroup = true
stdout_events_enabled = true
stderr_events_enabled = true

EOF

fi


if [ ! -z "$EXTRA_CMD" ]; then
    /bin/bash -c "$EXTRA_CMD"
fi
pip install -r /app/requirements.txt
if [ ! -z "$EXTRA_REQUIREMENTS" ]; then
    pip install $EXTRA_REQUIREMENTS
fi

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep nginx`" ] ; then
    echo "running nginx"
    nginx
fi

supervisord -c /etc/supervisor/supervisord.conf -n