#!/bin/bash
# ElonBot - AWS Ubuntu Server Setup Script
set -e

echo "=== 1. Tizim paketlari yangilanmoqda ==="
sudo apt update -y && sudo apt upgrade -y

echo "=== 2. Kerakli utilitalar va shriftlar o'rnatilmoqda ==="
sudo apt install -y python3 python3-pip python3-venv git fonts-dejavu fonts-liberation

echo "=== 3. Python venv yaratilmoqda ==="
python3 -m venv venv
source venv/bin/activate

echo "=== 4. Python kutubxonalari o'rnatilmoqda ==="
pip install --upgrade pip
pip install -r requirements.txt

echo "=== 5. Systemd xizmati sozlanmoqda ==="
sudo cp elonbot.service /etc/systemd/system/elonbot.service
sudo systemctl daemon-reload
sudo systemctl enable elonbot

echo "=== TAYYOR! ==="
echo "Endi .env faylini to'ldiring: nano .env"
echo "So'ngra botni ishga tushirish uchun: sudo systemctl start elonbot"
echo "Loglarni ko'rish uchun: sudo journalctl -u elonbot -f"
