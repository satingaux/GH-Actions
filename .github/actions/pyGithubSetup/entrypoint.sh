#!/bin/bash
set -e

echo Running the entrypoint.sh file
python -m pip install --upgrade pip setuptools wheel
pip install -r /requirements.txt

python /main.py
