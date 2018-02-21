#!/usr/bin/env bash

# This script allows trumppet-server to be used from anywhere. It is primarily
# invoked through a cron job to keep the tweet database up to date.

# Change directory to this script.
cd "$(dirname "$0")"

# Run trumppet-server through pipenv and pass through all arguments.
pipenv run trumppet-server "$@"
