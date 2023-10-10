#!/bin/sh

poetry install

if [ -f "python" ]
then
        poetry run python -m bdo_coupon_bot
else
        poetry run python3 -m bdo_coupon_bot
fi