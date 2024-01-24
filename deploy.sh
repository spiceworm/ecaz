#!/usr/bin/env bash

set -e

docker compose build

source .env

docker push registry.digitalocean.com/ecaz-xyz/app:${TAG}
