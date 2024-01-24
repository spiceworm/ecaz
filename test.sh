#!/usr/bin/env bash

set -e

docker compose -f test.yml down
docker compose -f test.yml up --build
