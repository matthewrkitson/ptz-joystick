#!/bin/bash

cd $(dirname $0)
source launcher/.venv/bin/activate

# We only need to do this once when we install the software
# TODO: Check for existence of a critical file, and only run this if it doesn't exist.
# pip install -r ../requirements.txt

# versions contains directory names of versions of the software
versions=("v1 Original" "v2 Mixer")
python3 launcher/menu.py "${versions[@]}"
index=$?
version="${versions[$index]}"

# Deactivate our current venv, and launch the correct app using it's own venv
deactivate
source "$version/.venv/bin/activate"
python3 "$version/app.py"
