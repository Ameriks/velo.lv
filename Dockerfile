FROM ameriks/django_webapp:latest

RUN git clone --depth=1 https://github.com/Ameriks/velo.lv.git /var/tmp/build/velo && \
	pip install -r /var/tmp/build/velo/requirements.txt && \
	rm -R /var/tmp/*