FROM java:jre-alpine

COPY install.sh /tmp/
RUN /tmp/install.sh

COPY ./s6 /etc/services.d

COPY config/elasticsearch.yml /opt/elasticsearch/config/elasticsearch.yml
COPY config/logstash.json /etc/logstash/logstash.json

COPY config/logstash/patterns /opt/logstash-2.3.2/patterns

# Specify Volume
VOLUME ["/var/lib/elasticsearch"]

# Exposes
EXPOSE 12201/udp 12202/udp 5601

ENV S6_KEEP_ENV 1
ENTRYPOINT ["/init"]
