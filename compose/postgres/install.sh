#!/bin/sh

set -e # fail on any error

apt-get update

apt-get install -y --no-install-recommends lzop pv libhiredis0.10 python3

# Install build packages
# ===================================================================
PACKAGES="make g++ python3-dev curl postgresql-server-dev-9.6 unzip libhiredis-dev libssl-dev libkrb5-dev"
apt-get install -y --no-install-recommends  ${PACKAGES}

curl -L https://github.com/2ndquadrant-it/redislog/archive/master.zip --insecure -o /tmp/master.zip
cd /tmp/
unzip master.zip
cd /tmp/redislog-master
make
make install

# Install Wal-E
# ===================================================================
curl https://bootstrap.pypa.io/get-pip.py --insecure -o /tmp/get-pip.py
python3 /tmp/get-pip.py
pip3 install gevent envdir boto
pip3 install pbr
pip3 install wal-e
umask u=rwx,g=rx,o= && mkdir -p /etc/wal-e.d/env && chown -R root:postgres /etc/wal-e.d

# Add Postgres config
# ===================================================================
cat /tmp/00_pg_config.conf >> /usr/share/postgresql/postgresql.conf.sample

# Clean up
# ===================================================================

apt-get purge -y --auto-remove ${PACKAGES}

apt-get clean
rm -rf /tmp/* /var/tmp/*
rm -rf /var/lib/apt/lists/*
