# docker-deb
My Docker setup for Debian hosts (includes docker, docker-compose, custom docker-gen, and a custom script to generate port forwardings)

This repo includes binaries from [Docker](https://www.docker.com),
a custom binary build from a [docker-gen](https://github.com/jwilder/docker-gen) fork with support for IPv6 addresses,
and some files from the [`debian.io` package in jessie-backports](https://packages.debian.org/jessie-backports/docker.io).

The repo also includes a custom script which generates port forwardings.<br>
I built this custom script because Dockers own iptables feature currently only supports IPv4 rules.
