FROM ameriks/postgres:9.5

COPY ./init-velo.sh /docker-entrypoint-initdb.d/velo.sh
RUN chmod +x /docker-entrypoint-initdb.d/velo.sh

#RUN sed -i "s/listen_addresses='localhost'/listen_addresses='localhost' -c ssl='off'/" /docker-entrypoint.sh
