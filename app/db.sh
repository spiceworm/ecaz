#!/usr/bin/env bash

# Helper script to connection to database in VPS

exec bash -c 'PGPASSWORD="${POSTGRES_PASSWORD}" psql --dbname="${POSTGRES_DB}" --host="${POSTGRES_HOST}" --port="${POSTGRES_PORT}" --set=sslmode=require --username="${POSTGRES_USER}"'
