#!/bin/bash

echo "Installing new changes, or resetting local changes."
git fetch
git reset --hard origin/master
poetry install

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Performing linux specific changes."
    chmod +x update.sh
    chmod +x launch.sh
fi