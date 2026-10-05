#!/bin/bash
# Debian / XFCE (X11) setup
sudo apt update
sudo apt install -y python3-venv python3-tk python3-dev scrot xclip xdotool wmctrl firefox-esr
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
echo "Done. Activate with: . .venv/bin/activate"
