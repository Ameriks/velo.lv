#!/bin/sh

set -e


echo "==============================================="
echo "VELO DEV INITDB"

psql --dbname="$POSTGRES_DB" <<-'EOSQL'
    CREATE ROLE velolv LOGIN ENCRYPTED PASSWORD 'md5fbda7efdf67b676179add83059545592' SUPERUSER INHERIT CREATEDB CREATEROLE NOREPLICATION;
    CREATE DATABASE velolv WITH OWNER = velolv;
EOSQL
