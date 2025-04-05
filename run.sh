bash
#!/bin/bash

# Virtual environment banaye agar nahi hai
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Virtual environment activate karo
source venv/bin/activate

# Dependencies install karo
pip3 install -r requirements.txt

# Purane gunicorn processes kill karo
pkill -9 gunicorn

# API start karo background mein
nohup gunicorn --workers 1 --bind 0.0.0.0:5000 app:app &

echo "API start ho gaya! Check karo: http://your-vps-ip:5000/generate?imageUrl=https://picsum.photos/512/512"
