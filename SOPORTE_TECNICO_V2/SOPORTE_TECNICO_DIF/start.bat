@echo off
echo ============================================
echo  SISTEMA SOPORTE TECNICO DIF - v2
echo ============================================
cd /d %~dp0
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Creando entorno virtual...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
)
echo Iniciando servidor Flask...
python app.py
pause
