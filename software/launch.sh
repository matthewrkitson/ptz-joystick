#!/bin/bash

cd $(dirname $0)
source .venv/bin/activate
pip install -r ../requirements.txt

if python3 button_21_pressed.py; then
    deactivate
    ../../ptz-joystick-v2/software/launch.sh
fi 

python3 app.py