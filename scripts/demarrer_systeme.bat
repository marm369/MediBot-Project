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

REM Verification de Streamlit
streamlit --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Installation de Streamlit...
    pip install streamlit
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
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo ⚠ Fichier requirements.txt non trouve, installation des dependances de base...
    pip install torch torchvision streamlit openai Pillow python-dotenv numpy
)

REM Verification du modele
if not exist "models\pneumonia_classifier_inference.pth" (
    echo ⚠ ATTENTION: Modele non trouve dans models\pneumonia_classifier_inference.pth
    echo 📝 Veuillez placer le modele entraine dans le dossier models\
    echo 📝 Ou executer l'entrainement avec: python src\training\train_model.py
)

REM Verification du fichier .env
if not exist ".env" (
    echo ⚠ Fichier .env non trouve
    if exist ".env.example" (
        copy .env.example .env
        echo 📝 Fichier .env cree depuis .env.example
        echo 📝 Veuillez configurer votre fichier .env avec votre cle API OpenAI
    ) else (
        echo ❌ Fichier .env.example non trouve
        echo 📝 Veuillez creer un fichier .env avec: OPENAI_API_KEY=votre_cle_api
    )
)

REM Demarrage du serveur MCP (si existe)
if exist "src\server\serveur_medical.py" (
    echo 🚀 Demarrage du serveur medical MCP...
    start "MediBot Server" cmd /k "python src\server\serveur_medical.py"
    timeout /t 3 /nobreak >nul
) else (
    echo ℹ Serveur MCP non trouve, demarrage de l'interface uniquement...
)

REM Demarrage de l'interface
echo 🌐 Demarrage de l'interface utilisateur...
streamlit run src\interface\interface_medibot.py

echo.
echo ✅ Systeme demarre avec succes!
echo 📍 Interface: http://localhost:8501
if exist "src\server\serveur_medical.py" (
    echo 📍 Serveur MCP: http://localhost:8000
)
echo.
echo Appuyez sur une touche pour fermer cette fenetre...
pause >nul