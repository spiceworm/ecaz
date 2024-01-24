#!/usr/bin/env bash

set -e

supervisorctl stop gunicorn

exec /usr/local/bin/gunicorn -c /etc/gunicorn.py 'application:create_app()'
