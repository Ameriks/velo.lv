FROM ameriks/django_geowebapp:latest

COPY ./requirements /tmp/requirements
RUN pip3 install -r /tmp/requirements/production.txt

COPY ./compose/django/s6 /etc/services.d

RUN rm -fr /tmp/*

WORKDIR /app
