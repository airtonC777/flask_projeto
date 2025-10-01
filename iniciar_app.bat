
@echo off
REM Inicia o app Flask e aguarda o servidor antes de abrir o navegador
start "" /B app_pagamentos.exe

:espera
REM Verifica se a porta 5000 está aberta
powershell -Command "try { $tcp = New-Object Net.Sockets.TcpClient('localhost', 5000); $tcp.Close(); exit 0 } catch { exit 1 }"
if %errorlevel% neq 0 (
    timeout /t 2 >nul
    goto espera
)

start "" http://127.0.0.1:5000
