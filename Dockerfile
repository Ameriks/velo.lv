FROM alpine:edge

ENV S6_KEEP_ENV 1

COPY ./requirements /tmp/requirements
COPY ./compose/django/base_install /tmp/install

RUN /tmp/install/install.sh

COPY ./compose/django/s6 /etc/services.d.installed

VOLUME ["/etc/services.d", "/var/run"]

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 5000
