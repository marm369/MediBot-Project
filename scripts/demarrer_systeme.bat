@echo off
chcp 65001
title MediBot - Systeme Medical IA

echo ========================================
echo    MEDIBOT - SYSTEME MEDICAL IA
echo ========================================
echo.

REM Verification de Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installe
    echo Veuillez installer Python 3.8+ depuis https://python.org
    pause
    exit /b 1
)

REM Creation de l'environnement virtuel
if not exist "venv" (
    echo 📦 Creation de l'environnement virtuel...
    python -m venv venv
)

REM Activation de l'environnement
echo 🔧 Activation de l'environnement...
call venv\Scripts\activate.bat

REM Installation des dependances
echo 📚 Installation des dependances...
pip install -r requirements.txt

REM Verification du fichier .env
if not exist ".env" (
    echo ⚠  Fichier .env non trouve, copie depuis .env.example...
    copy .env.example .env
    echo 📝 Veuillez configurer votre fichier .env avec vos cles API
)

REM Demarrage du serveur MCP
echo 🚀 Demarrage du serveur medical MCP...
start "MediBot Server" cmd /k "python src/server/serveur_medical.py"

REM Attente pour le demarrage du serveur
timeout /t 5 /nobreak

REM Demarrage de l'interface
echo 🌐 Demarrage de l'interface utilisateur...
start "MediBot Interface" cmd /k "streamlit run src/interface/interface_medibot.py"

echo.
echo ✅ Systeme demarre avec succes!
echo 📍 Serveur MCP: http://localhost:8000
echo 📍 Interface: http://localhost:8501
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul