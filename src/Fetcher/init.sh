#!/bin/bash

# Assumes init.sh has root privileges

set -e

apt install python3-pip
apt install python3
pip3 install -r requirements.txt
chmod +x main.py
python3 main.py
echo "successfully initialized Scheduler"
