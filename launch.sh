#!/bin/sh

. .venv/bin/activate # Assumes there's a virtual environment called .venv
pip install --upgrade --force-reinstall --no-cache-dir -r requirements.txt
python -m bdo_coupon_bot