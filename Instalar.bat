@echo off
cd /d "%~dp0"
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)"
if errorlevel 1 goto error
py -3 -m venv .venv
if errorlevel 1 goto error
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Instalacion completa. Abre Iniciar.bat.
pause
exit /b 0
:error
echo No se completo la instalacion. Comprueba que tengas Python 3.12 o posterior y tu conexion a Internet.
pause
exit /b 1
