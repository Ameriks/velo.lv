FROM mdillon/postgis:9.6

RUN localedef -i lv_LV -c -f UTF-8 -A /usr/share/locale/locale.alias lv_LV.UTF-8
ENV LANG lv_LV.utf8

COPY 00_pg_config.conf /tmp/
COPY install.sh /tmp/

COPY backup_db /etc/cron.daily/
RUN chmod +x /etc/cron.daily/backup_db

RUN /tmp/install.sh

COPY ./initdb-velo.sh /docker-entrypoint-initdb.d/velo.sh
RUN chmod +x /docker-entrypoint-initdb.d/velo.sh


VOLUME ["/run/postgresql", "/home/postgres"]
