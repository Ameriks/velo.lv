#!/bin/bash

set -ex

APP_COMPONENTS="$*"
CELERY_WORKERS=${CELERY_WORKERS:-4}
EXTRA_CMD=${EXTRA_CMD:-}
EXTRA_REQUIREMENTS=${EXTRA_REQUIREMENTS:-}

SUPERVISOR_CONF=/opt/supervisor.conf

echo "App Components: ${APP_COMPONENTS}"

cd /app
git pull

touch /var/log/django.log
chown nginx /var/log/django.log

# supervisor
cat << EOF > $SUPERVISOR_CONF
[supervisord]
nodaemon=false

[unix_http_server]
file=/var/run//supervisor.sock
chmod=0700

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run//supervisor.sock

EOF

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
stdout_logfile=/var/log/uwsgi.log
stderr_logfile=/var/log/uwsgi.log

EOF

fi

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep memcached`" ] ; then
    cat << EOF >> $SUPERVISOR_CONF
[program:memcached]
command=memcached -m 512 -u nobody -l 0.0.0.0 -I 10m
autostart=true
autorestart=true
user=root
priority=5
redirect_stderr=true
stdout_logfile=/var/log/memcached.log

EOF
fi

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep master-worker`" ] ; then
touch /var/log/celeryworker.log
chown nginx /var/log/celeryworker.log
    cat << EOF >> $SUPERVISOR_CONF
[program:master-worker]
priority=99
directory=/app/project
command=python manage.py celery worker -B -E -c ${CELERY_WORKERS} --uid=nginx --autoreload
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/celeryworker.log
stderr_logfile=/var/log/celeryworker.log

EOF
fi

if [ ! -z "`echo $APP_COMPONENTS | grep "^worker"`" ] ; then
touch /var/log/celeryworker.log
chown nginx /var/log/celeryworker.log
    cat << EOF >> $SUPERVISOR_CONF
[program:worker]
priority=99
directory=/app/project
command=python manage.py celery worker -E -c ${CELERY_WORKERS} --uid=nginx --autoreload
user=root
autostart=true
autorestart=true
stdout_logfile=/var/log/celeryworker.log
stderr_logfile=/var/log/celeryworker.log

EOF
fi

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep duplicity`" ] ; then
    cat << EOF >> /etc/cron.daily/duplicity
#!/bin/sh
duplicity --encrypt-key ${BACKUP_BUCKET_ENC_KEY} --exclude /mnt/velo_media/gallery --exclude /mnt/velo_media/easy_thumbnails --archive-dir /app/.duplicity/ --full-if-older-than 30D "/mnt/velo_media" ${BACKUP_BUCKET} > /var/log/duplicity.log
EOF
chmod +x /etc/cron.daily/duplicity

    cat << EOF >> $SUPERVISOR_CONF
[program:cron]
command = cron -f -L 15
startsecs = 5
stopwaitsecs = 3600
stopasgroup = false
killasgroup = true
stdout_logfile=/var/log/cron.log

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

supervisord -c $SUPERVISOR_CONF -n