#!/bin/bash

set -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd "${DIR}"

DOCKER_VERSION=1.8.2
COMPOSE_VERSION=1.4.2

wget -O src/usr/bin/docker https://get.docker.com/builds/Linux/x86_64/docker-${DOCKER_VERSION}
chmod a+x src/usr/bin/docker

wget -O src/usr/bin/docker-compose https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-Linux-x86_64
chmod a+x src/usr/bin/docker-compose
