#!/bin/sh

set -e


echo "==============================================="
echo "VELO INITDB"

psql --dbname="$POSTGRES_DB" <<-'EOSQL'
    CREATE ROLE velolv LOGIN ENCRYPTED PASSWORD 'md5fbda7efdf67b676179add83059545592' NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
    CREATE DATABASE velolv WITH OWNER = velolv ENCODING = 'UTF8' LC_COLLATE = 'lv_LV.utf8' LC_CTYPE = 'lv_LV.utf8';
EOSQL
psql --dbname="velolv" <<-'EOSQL'
    CREATE EXTENSION postgis;
EOSQL
