#!/bin/bash

# Assumes init.sh has root privileges

set -e

sudo apt update
sudo apt upgrade
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.10
sudo apt install python3-pip
sudo pip3 install accelerate
echo "Installing git, git lfs, and stable-diffusion-v1-5..."
sudo apt-get install git
git lfs install
git clone https://huggingface.co/runwayml/stable-diffusion-v1-5
echo "Complete."
sudo chmod +x main.py
sudo python3.10 main.py
echo "Successfully initialized Image Worker"