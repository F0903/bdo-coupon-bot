#!/bin/sh

. .venv/bin/activate # Assumes there's a virtual environment called .venv
pip install --upgrade -r requirements.txt
python -m bdo_coupon_bot