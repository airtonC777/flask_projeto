
@echo off
REM Gera executável único com PyInstaller
pip install pyinstaller
pyinstaller --onefile --name=app_pagamentos app.py
pause
