#!/bin/bash

if [[ $(git diff --name-only) ]]; then
    echo "Installing new changes."
    git reset --hard origin/master
    poetry install
fi

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    chmod +x update.sh
    chmod +x launch.sh
fi