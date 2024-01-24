#!/usr/bin/env bash

set -e

VERSION=0.1.0

docker compose build

docker tag ecaz_xyz-app:latest registry.digitalocean.com/ecaz-xyz/app:${VERSION}

docker push registry.digitalocean.com/ecaz-xyz/app:${VERSION}
