#!/bin/bash

cd $(dirname $0)
source .venv/bin/activate
pip install -r ../requirements.txt
python3 joystick.py