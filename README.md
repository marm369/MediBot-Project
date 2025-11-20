# MediBot – Assistant Médical Intelligent

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-orange)
![Streamlit](https://img.shields.io/badge/Interface-Streamlit-red)
![FastAPI](https://img.shields.io/badge/API-FastAPI-green)

**MediBot** est un système d'intelligence artificielle innovant qui combine vision par ordinateur et modèles de langage pour l'assistance au diagnostic médical.

## Fonctionnalités principales

### Analyse médicale avancée
- **Classification automatique** : Détection de pneumonie sur radiographies pulmonaires avec ResNet50
- **Précision élevée** : Modèle entraîné sur 5,863 images médicales annotées
- **Confiance mesurée** : Probabilités de prédiction et scores de confiance

### Assistant conversationnel intelligent
- **Explications détaillées** : Intégration GPT-4 pour des interprétations médicales pédagogiques
- **Réponses contextuelles** : Adaptation aux résultats d'analyse et questions utilisateur
- **Mode hors ligne** : Base de connaissances médicales prédéfinie en fallback

### Interface utilisateur optimisée
- **Interface intuitive** : Application Streamlit simple et épurée
- **Upload facile** : Glisser-déposer des radiographies
- **Historique conversationnel** : Suivi des analyses et discussions

## Installation

### Prérequis
- Python 3.8 ou supérieur
- 4GB RAM minimum
- Connexion internet (optionnel pour GPT-4)

### Installation pas à pas

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/marm369/MediBot-Project.git
   cd MediBot-Project
   ```
2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   # Activation selon votre OS
   source venv/bin/activate          # Linux/macOS
   venv\Scripts\activate            # Windows
3. **Configuration des variables d'environnement**
   ```bash
   cp .env.example .env
   ```
4. **Éditez le fichier .env et ajoutez :**
   ```bash
   OPENAI_API_KEY=votre_cle_api_ici
   MODEL_PATH=models/pneumonia_classifier_inference.pth
   MCP_SERVER_PORT=8000
   MAX_FILE_SIZE_MB=10
   ```
## Utilisation

### Démarrage rapide
```bash
scripts\demarrer_systeme.bat # Windows
scripts/demarrer_systeme.sh # Linux/macOS
```

### Démarrage manuel

1. **Lancer le serveur de classification (Terminal 1) :**
```bash
python src/server/serveur_medical.py
```

2. **Lancer l'interface utilisateur (Terminal 2) :**
```bash
streamlit run src/interface/interface_medibot.py
```

### Accéder aux interfaces :

Interface utilisateur : http://localhost:8501
API documentation : http://localhost:8000/docs

## Architecture du projet

```bash
MediBot-Project/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── server/
│   │   ├── __init__.py
│   │   └── serveur_medical.py
│   ├── chatbot/
│   │   ├── __init__.py
│   │   └── assistant_medical.py
│   └── interface/
│       ├── __init__.py
│       └── interface_medibot.py
├── models/
│   └── pneumonia_classifier_inference.pth
├── scripts/
│   ├── demarrer_systeme.bat
│   └── demarrer_systeme.sh
└── tests/
    └── __init__.py
