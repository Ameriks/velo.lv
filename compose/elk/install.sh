#!/bin/sh

apk add --update openssl nodejs curl bash
mkdir -p /opt

echo "[i] Installing s6 overlay"
curl -L https://github.com/just-containers/s6-overlay/releases/download/v1.17.2.0/s6-overlay-amd64.tar.gz --insecure -o /tmp/s6-overlay-amd64.tar.gz
tar xzf /tmp/s6-overlay-amd64.tar.gz -C /

echo "[i] Installing elasticsearch"
curl -L https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-2.3.3.tar.gz --insecure -o /tmp/elasticsearch.tar.gz
tar -xzf /tmp/elasticsearch.tar.gz -C /opt/
ln -s /opt/elasticsearch-2.3.3 /opt/elasticsearch
mkdir /var/lib/elasticsearch

echo "[i] Installing logstash"
curl -L https://download.elastic.co/logstash/logstash/logstash-2.3.2.tar.gz --insecure -o /tmp/logstash.tar.gz
tar -xzf /tmp/logstash.tar.gz -C /opt/
ln -s /opt/logstash-2.3.2 /opt/logstash
mkdir /etc/logstash

echo "[i] Installing kibana"
curl -L https://download.elastic.co/kibana/kibana/kibana-4.5.1-linux-x64.tar.gz --insecure -o /tmp/kibana.tar.gz
tar -xzf /tmp/kibana.tar.gz -C /opt/
ln -s /opt/kibana-4.5.1-linux-x64 /opt/kibana
rm -rf /opt/kibana-4.5.1-linux-x64/node/
mkdir -p /opt/kibana-4.5.1-linux-x64/node/bin/
ln -s $(which node) /opt/kibana/node/bin/node

echo "[i] Finishing"
rm -rf /tmp/* /var/cache/apk/*

echo "[i] Done"
