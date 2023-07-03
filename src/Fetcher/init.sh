#!/bin/bash

# Assumes init.sh has root privileges

set -e

sudo apt update
sudo apt upgrade

apt install python3-pip
apt install python3
pip3 install -r requirements.txt
chmod +x main.py
python3 main.py
echo "successfully initialized Scheduler"
