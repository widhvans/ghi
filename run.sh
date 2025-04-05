#!/bin/bash

# Virtual env banao agar nahi hai
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Virtual env activate karo
source venv/bin/activate

# Dependencies install karo
pip3 install -r requirements.txt

# Gunicorn se API chala
gunicorn --workers 1 --threads 4 --bind 0.0.0.0:8080 --timeout 600
