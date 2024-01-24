#!/usr/bin/env bash

set -e

TAG=0.1.0

retry_flag=''

print_usage() {
    printf "Usage: ./deploy.sh [-r] \n"
}

while getopts 'r' flag; do
    case "${flag}" in
        r) retry_flag='true' ;;
        *) print_usage
            exit 1 ;;
    esac
done

if [ "$retry_flag" = true ] ; then
    docker push registry.digitalocean.com/ecaz-xyz/app:${TAG}
else
    docker compose build --no-cache
    docker tag registry.digitalocean.com/ecaz-xyz/app:latest registry.digitalocean.com/ecaz-xyz/app:${TAG}
    docker push registry.digitalocean.com/ecaz-xyz/app:${TAG}
fi
