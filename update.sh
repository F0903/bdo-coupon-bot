#!/bin/sh

git fetch --all
if [[ `git status --porcelain` ]]; then
    git reset --hard origin/master
    poetry install
fi
