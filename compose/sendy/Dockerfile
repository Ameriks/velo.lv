FROM ameriks/php-fpm:latest

ADD nginx.conf /etc/nginx/

RUN echo "*/5     *       *       *       *       php /app/scheduled.php > /dev/null 2>&1" >> /etc/crontabs/root
RUN echo "*/1     *       *       *       *       php /app/autoresponders.php > /dev/null 2>&1" >> /etc/crontabs/root

COPY run-pre.sh /
RUN chmod +x /run-pre.sh
