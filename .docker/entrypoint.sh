#!/bin/bash
export DB_NAME=$1
export DB_USER=$2
export DB_PASSWORD=$3
export DB_IP_ADDRESS=$4
export DB_PORT=$5
export DB_ENGINE=$6
echo "DB_NAME: $DB_NAME"
echo "DB_USER: $DB_USER"
echo "DB_PASSWORD: $DB_PASSWORD"
echo "DB_IP_ADDRESS: $DB_IP_ADDRESS"
echo "DB_PORT: $DB_PORT"
echo "DB_ENGINE: $DB_ENGINE"
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
