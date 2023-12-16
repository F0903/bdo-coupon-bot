#!/bin/bash

if [[ $(git fetch) ]]; then
    echo "Installing new changes"
    git reset --hard origin/master
    poetry install
fi
