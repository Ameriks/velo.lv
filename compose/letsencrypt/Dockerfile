FROM alpine:edge

RUN apk -U add certbot && rm -f /var/cache/apk/*

COPY renewcerts /etc/periodic/weekly/
# Add cron scripts

CMD ["crond", "-f", "-d", "8"]

#  certbot certonly -a webroot --webroot-path=/var/lib/app/letsencrypt -d www.velo.lv -d velo.lv -d mans.velo.lv -d sendy.velo.lv -d test.velo.lv -d logs.velo.lv
# export TERM=xterm
