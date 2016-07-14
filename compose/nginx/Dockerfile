FROM nginx:stable-alpine

COPY conf /etc/nginx

RUN apk -U add openssl && rm -f /var/cache/apk/*

RUN mkdir /etc/nginx/ssl
RUN openssl dhparam -out /etc/nginx/ssl/dhparams.pem 2048
