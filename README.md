🫁 MediBot – Assistant Médical Intelligent
[Python](https://www.python.org/) | [License](LICENSE) | Version 1.0.0
MediBot est un système d’intelligence artificielle innovant qui combine : 
- Vision par ordinateur : utilisation de ResNet50 pour la classification des radiographies pulmonaires. 
- Modèle de langage GPT-4 : génération d’explications médicales détaillées et compréhensibles. 
- Interface conviviale Streamlit : pour une interaction simple et intuitive avec l’utilisateur.
🚀 Fonctionnalités principales
- Analyse d’images médicales : détection automatique de la pneumonie sur radiographies. 
- Explications intelligentes : GPT-4 fournit des interprétations détaillées et pédagogiques. 
- Interface simple : utilisateur guidé à travers une interface Streamlit épurée.
🛠️ Installation
1. Clonez le dépôt : 
   git clone https://github.com/marm369/MediBot-Project.git 
   cd MediBot-Project 
 
2. Créez un environnement virtuel : 
   python -m venv venv 
   source venv/bin/activate  # Linux/macOS 
   venv\Scripts\activate   # Windows 
 
3. Installez les dépendances : 
   pip install -r requirements.txt 
 
4. Configurez vos variables d’environnement : 
   cp .env.example .env 
   # puis ajoutez votre clé OpenAI dans .env
💡 Utilisation
Démarrez le système avec : 
# Windows 
scripts\demarrer_systeme.bat 
 
# Linux/macOS 
bash scripts/demarrer_systeme.sh 
 
Ouvrez ensuite l’interface Streamlit : 
streamlit run src/interface/interface_medibot.py
📁 Architecture du projet
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
├── tests/ 
│   └── __init__.py 
└── assets/ 
    └── images/ 
        └── logo.png
📄 License
Ce projet est sous MIT License. Voir le fichier LICENSE pour plus d’informations.
✨ Capture d’écran ()
![Logo MediBot](assets/images/logo.png)
