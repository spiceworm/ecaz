#!/usr/bin/env bash

mkdir -p /var/log/supervisor/{gunicorn,nginx}

counter=0
until pg_isready --dbname="${POSTGRES_DB}" --host="${POSTGRES_HOST}" --port="${POSTGRES_PORT}" --username="${POSTGRES_USER}";
do
  ((counter++))
  echo "Waiting for postgres to accept connections: attempt ${counter}" | tee /var/log/entrypoint.log
  sleep 1;
done;

echo "Applying database migrations"
flask db upgrade

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
