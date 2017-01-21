#!/bin/sh

set -ex

adduser -D -u 9005 django

apk -U add python3 python3-dev musl musl-dev postgresql-dev gcc \
           libxml2-dev libxslt-dev \
           freetype libwebp libffi libwebp libxslt openjpeg giflib postgresql-client libpng libxml2 lcms2 lcms2-utils tiff libjpeg-turbo libgcrypt libgpg-error libpq libedit \
           zlib-dev tiff-dev lcms2-dev libwebp-dev freetype-dev giflib-dev libjpeg-turbo-dev openjpeg-dev \
           libffi-dev gettext s6 make openssl git libstdc++ optipng openssh-client \
           libc-dev file geoip

# Install latest geoip dat file in /usr/share/GeoIP/GeoIP.dat

wget -q  http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz -O /tmp/GeoLite2-City.mmdb.gz
gunzip /tmp/GeoLite2-City.mmdb.gz
mv /tmp/GeoLite2-City.mmdb /usr/share/GeoIP/

wget -q  http://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.mmdb.gz -O /tmp/GeoLite2-Country.mmdb.gz
gunzip /tmp/GeoLite2-Country.mmdb.gz
mv /tmp/GeoLite2-Country.mmdb /usr/share/GeoIP/

# END Install

pip3 install -U pip

apk add --update --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ jpegoptim gdal geos proj4

ln -s /lib/libz.so /usr/lib/
ln -s /usr/bin/python3 /usr/bin/python

# S6 overlay
wget https://github.com/just-containers/s6-overlay/releases/download/v1.18.1.5/s6-overlay-amd64.tar.gz -O /tmp/s6-overlay-amd64.tar.gz
tar xzf /tmp/s6-overlay-amd64.tar.gz -C /

cp /tmp/install/init-stage3 /etc/s6/init/init-stage3

pip3 install -r /tmp/requirements/production.txt

apk del zlib-dev libpng-dev freetype-dev libjpeg-turbo-dev tiff-dev lcms2-dev libffi-dev libwebp-dev libxml2-dev libxslt-dev musl-dev openjpeg-dev openssl-dev postgresql-dev postgresql giflib-dev python3-dev
apk del binutils-libs binutils gmp isl libgomp libatomic libgcc pkgconf pkgconfig mpfr3 mpc1 gcc make

cp /tmp/install/entrypoint.sh /

rm -f /var/cache/apk/*
rm -R /tmp/*
