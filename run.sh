#!/bin/bash
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip3 install -r requirements.txt
nohup gunicorn --workers 1 --threads 4 --bind 0.0.0.0:5000 --timeout 600
