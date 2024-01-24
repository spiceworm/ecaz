#!/usr/bin/env bash

# Helper script to connection to database in VPS

CMD="PGPASSWORD=${POSTGRES_PASSWORD} psql --dbname=${POSTGRES_DB} --host=${POSTGRES_HOST} --port=${POSTGRES_PORT} --set=sslmode=require --username=${POSTGRES_USER}"

if [ $# -eq 0 ]
  then
    # No args provided. Connect to db
    exec bash -c "${CMD}"
  else
    # Pass args to psql and execute in db container
    bash -c "${CMD} --command '$*'";
fi
