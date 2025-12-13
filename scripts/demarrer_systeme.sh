#!/bin/bash

echo "========================================"
echo "   MEDIBOT - SYSTEME MEDICAL IA"
echo "========================================"
echo

# Verification de Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installe"
    echo "Veuillez installer Python 3.8+"
    exit 1
fi

# Creation de l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "📦 Creation de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activation de l'environnement
echo "🔧 Activation de l'environnement..."
source venv/bin/activate

# Installation des dependances
echo "📚 Installation des dependances..."
pip install -r requirements.txt

# Verification du fichier .env
if [ ! -f ".env" ]; then
    echo "⚠  Fichier .env non trouve, copie depuis .env.example..."
    cp .env.example .env
    echo "📝 Veuillez configurer votre fichier .env avec vos cles API"
fi

# Demarrage du serveur MCP
echo "🚀 Demarrage du serveur medical MCP..."
gnome-terminal -- bash -c "python src/server/serveur_medical.py; exec bash" 2>/dev/null \
|| xterm -e "python src/server/serveur_medical.py; exec bash" 2>/dev/null \
|| echo "❌ Impossible de lancer un nouveau terminal. Demarrez manuellement: python src/server/serveur_medical.py"

# Attente pour le demarrage du serveur
sleep 5

# Demarrage de l'interface
echo "🌐 Demarrage de l'interface utilisateur..."
streamlit run src/interface/interface_medibot.py &

echo
echo "✅ Systeme demarre avec succes!"
echo "📍 Serveur MCP: http://localhost:8000"
echo "📍 Interface: http://localhost:8501"
echo
echo "Appuyez sur Ctrl+C pour arreter le systeme"
wait