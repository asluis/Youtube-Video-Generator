#!/bin/bash

set -e

MYSQL_ROOT_PASSWORD="root"

sudo apt update
sudo apt upgrade -y

sudo DEBIAN_FRONTEND=noninteractive apt-get -y install mysql-server
sudo service mysql start

mysql -u root -p"${MYSQL_ROOT_PASSWORD}" < database_init.sql
