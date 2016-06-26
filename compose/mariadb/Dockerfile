FROM alpine:edge

ENV LANG="lv_LV.UTF-8" \
    LC_ALL="lv_LV.UTF-8" \
    LANGUAGE="lv_LV.UTF-8"

RUN apk -U upgrade && \
    apk --update add \
      mariadb mariadb-client \
      && \
      rm -rf /tmp/src && \
      rm -rf /var/cache/apk/*

ADD my.cnf /etc/mysql/my.cnf
ADD start.sh /start.sh

RUN chmod u+x /start.sh

VOLUME ["/data"]
EXPOSE 3306

CMD ["/start.sh"]
