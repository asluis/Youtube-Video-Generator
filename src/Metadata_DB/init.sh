#!/bin/bash

set -e

MYSQL_ROOT_PASSWORD="root"

sudo apt update
sudo apt upgrade -y

sudo DEBIAN_FRONTEND=noninteractive apt-get -y install mysql-server
sudo service mysql start

mysql -u root -p"${MYSQL_ROOT_PASSWORD}" < database_init.sql

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11

sudo apt install python3-pip
sudo pip3 install -r requirements.txt # Assumes .txt file exists.

sudo chmod +x main.py
echo "Successfully initialized Metadata Database"
python3.11 main.py