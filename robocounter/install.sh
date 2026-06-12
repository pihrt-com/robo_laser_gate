#!/bin/bash

set -e

echo "Aktualizace balíčků..."
sudo apt update

echo "Instalace balíčků..."
sudo apt install -y \
    python3-flask \
    python3-requests \
    pigpio \
    python3-pigpio \
    nginx \
    network-manager

echo "Povolení služeb..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

sudo systemctl enable nginx
sudo systemctl start nginx

echo "Vytvářím sudoers pravidla..."

sudo tee /etc/sudoers.d/robocounter >/dev/null <<EOF
pi ALL=(ALL) NOPASSWD: /usr/sbin/reboot
pi ALL=(ALL) NOPASSWD: /usr/sbin/shutdown
pi ALL=(ALL) NOPASSWD: /bin/systemctl
pi ALL=(ALL) NOPASSWD: /usr/bin/nmcli
EOF

sudo chmod 0440 /etc/sudoers.d/robocounter

echo "Kontrola sudoers..."
sudo visudo -c

echo "Kontrola sudo oprávnění..."

sudo -n reboot --help >/dev/null
echo "reboot OK"

sudo -n shutdown --help >/dev/null
echo "shutdown OK"

sudo -n systemctl --version >/dev/null
echo "systemctl OK"

sudo -n nmcli --version >/dev/null
echo "nmcli OK"

echo ""
echo "Kontrola Flask:"
python3 -c "import flask; print('Flask OK')"

echo ""
echo "Kontrola requests:"
python3 -c "import requests; print('requests OK')"

echo ""
echo "Kontrola pigpio:"
python3 -c "import pigpio; print('pigpio OK')"

echo ""
echo "Kontrola sudo nmcli:"
sudo -n nmcli connection show >/dev/null
echo "nmcli OK"

echo ""
echo "Instalace dokončena."
