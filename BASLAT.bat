@echo off
cd /d "%~dp0"
echo Afet Atlas baslatiliyor...
python -m streamlit run app.py
if errorlevel 1 (
    echo.
    echo Uygulama acilamadi. Gerekli paketleri yuklemek icin:
    echo python -m pip install -r requirements.txt
    pause
)
