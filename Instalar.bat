@echo off
cd /d "%~dp0"
py -3 -m venv .venv
if errorlevel 1 goto error
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Instalacion completa. Abre Iniciar.bat.
pause
exit /b 0
:error
echo No se completo la instalacion. Comprueba Python y tu conexion a Internet.
pause
exit /b 1
