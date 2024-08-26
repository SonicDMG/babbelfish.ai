#!/bin/sh

set -eux -o pipefail

if [[ ! -e .env ]]; then
    cp .env.example .env
fi

./python-install.sh
./npm-install.sh
