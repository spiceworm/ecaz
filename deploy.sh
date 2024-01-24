#!/usr/bin/env bash

set -e

docker compose build --no-cache

source .env

docker push registry.digitalocean.com/ecaz-xyz/app:${TAG}
