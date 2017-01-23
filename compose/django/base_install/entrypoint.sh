#!/bin/sh

set -ex

APP_COMPONENTS="$*"
echo "App Components: ${APP_COMPONENTS}"

rm -fR /etc/services.d/*

if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep gunicorn`" ] ; then
    cp -R /etc/services.d.installed/gunicorn /etc/services.d/
fi
if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep celeryworker`" ] ; then
    cp -R /etc/services.d.installed/celeryworker /etc/services.d/
fi
if [ -z "$APP_COMPONENTS" ] || [ ! -z "`echo $APP_COMPONENTS | grep celerybeat`" ] ; then
    cp -R /etc/services.d.installed/celerybeat /etc/services.d/
fi


##
## load default PATH (the same that Docker includes if not provided) if it doesn't exist,
## then go ahead with stage1.
## this was motivated due to this issue:
## - https://github.com/just-containers/s6-overlay/issues/108
##

exec "/init"
