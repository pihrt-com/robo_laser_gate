#!/bin/bash

sudo apt update

sudo apt install -y \
    python3-flask \
    pigpio \
    python3-pigpio \
    nginx \
    network-manager

sudo systemctl enable pigpiod
sudo systemctl start pigpiod

sudo systemctl enable nginx
sudo systemctl start nginx

echo ""
echo "Kontrola Flask:"
python3 -c "import flask; print('Flask OK')"

echo ""
echo "Kontrola pigpio:"
python3 -c "import pigpio; print('pigpio OK')"

echo ""
echo "Instalace dokončena."