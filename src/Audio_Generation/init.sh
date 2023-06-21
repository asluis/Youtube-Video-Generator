#!/bin/bash

# Assumes init.sh has root privileges

set -e

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.10
sudo apt install python3-pip
sudo pip3 install -r requirements.txt
sudo chmod +x main.py
sudo python3.10 main.py
echo "Successfully initialized Audio Worker"