import streamlit as st
import os
import sys
from PIL import Image
import io
import logging
import requests

# Ajouter le chemin source
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(_file_))))

from src.chatbot.assistant_medical import AssistantMedicalGPT

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

class InterfaceMediBot:
    def _init_(self):
        self.assistant = None
        self._initialiser_page()
        self._initialiser_assistant()

    def _initialiser_page(self):
        """Configure la page Streamlit"""
        st.set_page_config(
            page_title="MediBot - Assistant Médical IA",
            page_icon="🏥",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # CSS personnalisé
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .warning-box {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .success-box {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 5px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .chat-user {
            background-color: #e3f2fd;
            padding: 0.5rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        .chat-bot {
            background-color: #f8f9fa;
            padding: 0.5rem;
            border-radius: 10px;
            margin: 0.5rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

    def _initialiser_assistant(self):
        """Initialise l'assistant médical"""
        try:
            self.assistant = AssistantMedicalGPT()
            st.sidebar.success("✅ Assistant médical initialisé")
        except Exception as e:
            st.sidebar.error(f"❌ Erreur initialisation: {e}")
            self.assistant = None

    def _verifier_serveur_mcp(self):
        """Vérifie la connexion au serveur MCP"""
        if self.assistant:
            return self.assistant._check_mcp_server()
        return False

    def afficher_entete(self):
        """Affiche l'en-tête de l'application"""
        st.markdown('<h1 class="main-header">🏥 MediBot - Assistant Médical IA</h1>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            *Votre assistant virtuel pour l'analyse des radiographies pulmonaires*  
            Classification automatique des pneumonies avec explications détaillées
            """)

    def afficher_avertissement(self):
        """Affiche l'avertissement médical"""
        st.markdown("""
        <div class="warning-box">
        <h4>⚠ AVERTISSEMENT IMPORTANT</h4>
        <p>Ce système est un <strong>outil d'aide à la décision</strong> et ne remplace pas un diagnostic médical professionnel.</p>
        <p><strong>Consultez toujours un médecin qualifié</strong> pour toute décision médicale importante.</p>
        </div>
        """, unsafe_allow_html=True)

    def afficher_sidebar(self):
        """Affiche la barre latérale avec les informations système"""
        with st.sidebar:
            st.header("🔧 État du Système")
            
            # Statut serveur MCP
            if self._verifier_serveur_mcp():
                st.success("✅ Serveur médical connecté")
            else:
                st.error("❌ Serveur médical hors ligne")
                st.info("Démarrez le serveur avec: python src/server/serveur_medical.py")

            # Statut OpenAI
            if self.assistant and self.assistant.openai_api_key:
                st.success("✅ API OpenAI configurée")
            else:
                st.warning("⚠ Clé API OpenAI manquante")
                st.info("Ajoutez votre clé dans le fichier .env")

            st.markdown("---")
            st.header("📖 Guide d'utilisation")
            
            st.markdown("""
            1. *Téléchargez* une radiographie pulmonaire
            2. *Analyse automatique* par l'IA
            3. *Obtenez une explication* détaillée
            4. *Posez des questions* sur les résultats
            
            *Formats supportés:* JPEG, PNG, DICOM
            *Taille max:* 10MB
            """)

            st.markdown("---")
            st.header("ℹ À propos")
            st.markdown("""
            *MediBot* utilise:
            - *ResNet50* pour la classification
            - *GPT-4* pour les explications
            - *FastAPI* pour le serveur médical
            - *Streamlit* pour l'interface
            """)

    def section_upload_image(self):
        """Section pour le téléchargement d'image"""
        st.header("📤 Télécharger une Radiographie")
        
        uploaded_file = st.file_uploader(
            "Choisissez une image de radiographie pulmonaire",
            type=['jpg', 'jpeg', 'png', 'dcm'],
            help="Formats supportés: JPEG, PNG, DICOM"
        )
        
        if uploaded_file is not None:
            # Afficher l'image
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Radiographie téléchargée", use_column_width=True)
                
                # Convertir en bytes
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='JPEG')
                img_bytes = img_bytes.getvalue()
                
                return img_bytes, uploaded_file.name
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement de l'image: {e}")
                return None, None
        
        return None, None

    def section_analyse(self, image_bytes, filename):
        """Section pour l'analyse d'image"""
        if image_bytes and self.assistant:
            st.header("🔍 Analyse en Cours")
            
            with st.spinner("🤖 Analyse de la radiographie par l'IA médicale..."):
                try:
                    # Analyse avec l'assistant
                    resultat = self.assistant.analyser_image(image_bytes)
                    
                    # Afficher le résultat
                    st.markdown("### 📊 Résultats de l'Analyse")
                    st.markdown(f'<div class="success-box">{resultat}</div>', unsafe_allow_html=True)
                    
                    return True
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors de l'analyse: {e}")
                    return False
        return False

    def section_chat(self):
        """Section de chat pour les questions"""
        st.header("💬 Dialogue avec MediBot")
        
        # Initialisation de l'historique de chat
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Affichage de l'historique
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Input utilisateur
        if prompt := st.chat_input("Posez une question sur les pneumonies..."):
            # Ajouter le message utilisateur
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Réponse de l'assistant
            if self.assistant:
                with st.chat_message("assistant"):
                    with st.spinner("🤖 Réflexion..."):
                        try:
                            response = self.assistant.chat_direct(prompt)
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        except Exception as e:
                            error_msg = f"❌ Erreur: {str(e)}"
                            st.error(error_msg)
            else:
                st.error("❌ Assistant non disponible")

    def lancer_interface(self):
        """Lance l'interface principale"""
        self.afficher_entete()
        self.afficher_avertissement()
        self.afficher_sidebar()
        
        # Sections principales
        tab1, tab2, tab3 = st.tabs(["📊 Analyse Radiographie", "💬 Chat Médical", "📚 Informations"])
        
        with tab1:
            st.header("Analyse de Radiographies")
            image_bytes, filename = self.section_upload_image()
            if image_bytes:
                self.section_analyse(image_bytes, filename)
        
        with tab2:
            self.section_chat()
        
        with tab3:
            st.header("📚 Informations sur la Pneumonie")
            st.markdown("""
            ### Qu'est-ce que la pneumonie?
            
            La pneumonie est une infection des poumons qui peut être causée par:
            
            *🦠 Causes bactériennes:*
            - Streptococcus pneumoniae (le plus courant)
            - Haemophilus influenzae
            - Legionella pneumophila
            
            *🦠 Causes virales:*
            - Virus respiratoire syncytial (VRS)
            - Grippe (influenza)
            - SARS-CoV-2 (COVID-19)
            
            *🔍 Symptômes courants:*
            - Toux (sèche ou productive)
            - Fièvre et frissons
            - Difficultés respiratoires
            - Douleur thoracique
            - Fatigue
            
            *📊 Diagnostic:*
            - Examen clinique
            - Radiographie pulmonaire
            - Analyses sanguines
            - Culture des expectorations
            
            *💊 Traitements:*
            - Antibiotiques (pour les bactéries)
            - Antiviraux (pour les virus)
            - Médicaments contre la fièvre
            - Repos et hydratation
            """)

def main():
    """Fonction principale"""
    interface = InterfaceMediBot()
    interface.lancer_interface()

if _name_ == "_main_":
    main()