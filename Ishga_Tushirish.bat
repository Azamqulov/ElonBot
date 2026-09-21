@echo off
chcp 65001 > nul
title ElonBot - Telegram Vakansiya Boti
color 0A

echo ======================================================
echo           ELONBOT - ISHGA TUSHIRISH PANELI
echo ======================================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo [XATO] Virtual muhit (venv) topilmadi!
    echo Iltimos, avval python -m venv venv orqali muhit yarating.
    pause
    exit /b 1
)

echo [1/2] Virtual muhit faollashtirilmoqda...
call venv\Scripts\activate.bat

echo [2/2] ElonBot ishga tushirilmoqda...
echo.
echo Botni to'xtatish uchun: Ctrl + C
echo ======================================================
echo.

python -u main.py

echo.
echo Bot faoliyati to'xtatildi.
pause
