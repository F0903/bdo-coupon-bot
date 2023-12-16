#!/bin/sh

if [[ `git fetch --porcelain` ]]; then
    git reset --hard origin/master
    poetry install
fi
