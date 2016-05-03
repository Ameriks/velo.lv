FROM ameriks/django_geowebapp:latest

COPY ./requirements /tmp/requirements
RUN pip3 install -r /tmp/requirements/production.txt

COPY ./compose/django/gunicorn.sh /gunicorn.sh
COPY ./compose/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN sed -i 's/\r//' /gunicorn.sh
RUN chmod +x /entrypoint.sh
RUN chmod +x /gunicorn.sh

RUN rm -fr /tmp/*

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
