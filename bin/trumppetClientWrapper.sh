#!/usr/bin/env bash

# This script allows trumppet-client to be used from anywhere.

# Change directory to this script.
cd "$(dirname "$0")"

# Run trumppet-client through pipenv and pass through all arguments.
pipenv run trumppet-client "$@"
