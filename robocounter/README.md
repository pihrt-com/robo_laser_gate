Install:
sudo bash install.sh

sudo cp casomira.service \
/etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable casomira
sudo systemctl start casomira
sudo systemctl stop casomira

user: pi
pass: robocounter

--------------
Internet/LAN
      ↓
Nginx :80
      ↓
127.0.0.1:5000
      ↓
Flask

--------------
Zapnu zařízení
      ↓
pokus o klientskou WiFi (STA)
      ↓
30 sec timeout
      ↓
automaticky vytvoří Wi-Fi (AP)
SSID: ROBOCOUNTER
PASS: 12345678
192.168.4.1

--------------
limit 5000 uložených jízd
konfigurace buzzeru
konfigurace debounce
konfigurace Active LOW/HIGH
nejlepší čas
poslední čas
API data pro web
posledních 50 výsledků
nejnovější nahoře
živý čas při měření
nejlepší čas
export CSV
reset historie
čtení konfigurace
ukládání konfigurace
export konfigurace
systémové informace
restart aplikace
restart Raspberry
vypnutí Raspberry

Vyžaduje:
Nginx
Flask
pigpio

API:
GET  /api/results
GET  /api/config
POST /api/config

POST /api/reset
GET  /api/export

POST /api/reboot
POST /api/shutdown

GET  /api/system

POST /api/wifi/ap
POST /api/wifi/client
