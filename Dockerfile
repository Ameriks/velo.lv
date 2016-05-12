FROM ameriks/django_geowebapp:latest

COPY ./requirements /tmp/requirements
RUN pip3 install -r /tmp/requirements/production.txt

COPY ./compose/django/entrypoint.sh /entrypoint.sh

COPY ./compose/django/s6 /etc/s6

RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN rm -fr /tmp/*

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
