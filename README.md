\# 🫁 MediBot - Assistant Médical Intelligent



MediBot est un système d'intelligence artificielle qui combine un modèle de vision par ordinateur (ResNet50) pour la classification des radiographies pulmonaires et un modèle de langage (GPT-4) pour générer des explications médicales.



\## 🚀 Fonctionnalités



\- \*Analyse de radiographies pulmonaires\* : Détection de la pneumonie à partir d'images de radiographies.

\- \*Explications détaillées\* : Génération d'explications médicales par GPT-4.

\- \*Interface conviviale\* : Interface Streamlit simple et intuitive.



\## 📁 Structure du projet

MediBot-Project/

│

├── README.md

├── requirements.txt

├── .env.example

├── .gitignore

│

├── src/

│   ├── \_init\_.py

│   ├── server/

│   │   ├── \_init\_.py

│   │   └── serveur\_medical.py

│   ├── chatbot/

│   │   ├── \_init\_.py

│   │   └── assistant\_medical.py

│   └── interface/

│       ├── \_init\_.py

│       └── interface\_medibot.py

│

├── models/

│   └── pneumonia\_classifier\_inference.pth

│

├── scripts/

│   ├── demarrer\_systeme.bat

│   └── demarrer\_systeme.sh

│

├── tests/

│   └── \_init\_.py

│

└── assets/

&nbsp;   └── images/

&nbsp;       └── logo.png

