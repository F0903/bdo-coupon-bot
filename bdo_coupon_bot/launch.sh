#!/bin/sh

. .venv/bin/activate # Assumes there's a virtual environment called .venv
pip install -r requirements.txt
python -m bdo_coupon_bot