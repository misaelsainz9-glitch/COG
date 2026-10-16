@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Preparar-SASISOPA.ps1"
set "resultado=%errorlevel%"
if not "%resultado%"=="0" echo No se completo la preparacion. Revisa el mensaje anterior.
pause
exit /b %resultado%
