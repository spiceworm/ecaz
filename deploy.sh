#!/usr/bin/env bash

set -e

TAG=0.1.0

docker compose build --no-cache
docker tag registry.digitalocean.com/ecaz-xyz/app:latest registry.digitalocean.com/ecaz-xyz/app:${TAG}
docker push registry.digitalocean.com/ecaz-xyz/app:${TAG}
