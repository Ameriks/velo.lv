FROM ameriks/postgres:9.5

COPY ./init-velo.sh /docker-entrypoint-initdb.d/velo.sh
RUN chmod +x /docker-entrypoint-initdb.d/velo.sh

COPY postgresql.conf /usr/share/postgresql/postgresql.conf.sample
