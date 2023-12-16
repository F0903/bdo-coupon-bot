#!/bin/bash

if [[ $(git fetch) ]]; then
    git reset --hard origin/master
    poetry install
fi
