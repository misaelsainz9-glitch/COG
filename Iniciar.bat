@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
 echo Ejecuta Instalar.bat primero.
 pause
 exit /b 1
)
.venv\Scripts\python.exe basico.py
if errorlevel 1 pause
