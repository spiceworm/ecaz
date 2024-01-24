#!/usr/bin/env bash

set -e

export TOX_ARGS="$*"

docker compose -f test.yml down
docker compose -f test.yml up --build
