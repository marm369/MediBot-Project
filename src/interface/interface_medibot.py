import streamlit as st
import os
import sys
from PIL import Image
import io
import logging
import base64
import requests

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterfaceMediBot:
    def __init__(self):
        self._initialiser_page()
        self._initialiser_session()

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
            margin-bottom: 1rem;
        }
        .warning-box {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .success-box {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .chat-user {
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            border: 1px solid #bbdefb;
        }
        .chat-bot {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            border: 1px solid #e9ecef;
        }
        .upload-section {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border: 2px dashed #dee2e6;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

    def _initialiser_session(self):
        """Initialise les variables de session"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_image" not in st.session_state:
            st.session_state.current_image = None
        if "image_uploaded" not in st.session_state:
            st.session_state.image_uploaded = False

    def afficher_entete(self):
        """Affiche l'en-tête de l'application"""
        st.markdown('<h1 class="main-header">🏥 MediBot - Assistant Médical IA</h1>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            Votre assistant intelligent pour l'analyse des radiographies et questions médicales  
            Combinaison d'IA spécialisée et d'explications intelligentes
            """)

    def afficher_avertissement(self):
        """Affiche l'avertissement médical"""
        st.markdown("""
        <div class="warning-box">
        <h4>⚠ AVERTISSEMENT MÉDICAL IMPORTANT</h4>
        <p>Ce système est un <strong>outil d'aide à la décision</strong> et ne remplace pas un diagnostic médical professionnel.</p>
        <p><strong>Consultez toujours un médecin qualifié</strong> pour toute décision médicale importante.</p>
        <p><strong>En cas d'urgence médicale, appelez le 15 (SAMU) immédiatement.</strong></p>
        </div>
        """, unsafe_allow_html=True)

    def afficher_sidebar(self):
        """Affiche la barre latérale avec les informations système"""
        with st.sidebar:
            st.header("🔧 État du Système")
            
            # Test de connexion au serveur
            try:
                response = requests.get("http://localhost:8000/health")
                if response.status_code == 200:
                    st.success("✅ Serveur de classification connecté")
                else:
                    st.error("❌ Serveur de classification hors ligne")
            except:
                st.error("❌ Serveur de classification non accessible")
                st.info("Démarrez le serveur avec: python serveur_medical.py")

            st.markdown("---")
            st.header("💡 Comment utiliser")
            
            st.markdown("""
            📤 Pour analyser une image:
            1. Téléchargez une radiographie
            2. Posez votre question dans le chat
            3. L'IA analysera l'image automatiquement

            💬 Pour poser des questions:
            • Symptômes de pneumonie
            • Causes et traitements
            • Informations médicales générales

            🖼 Formats supportés: JPEG, PNG
            """)

            st.markdown("---")
            st.header("🦠 À propos de la pneumonie")
            st.markdown("""
            Signes radiologiques:
            • Opacités alvéolaires
            • Consolidations
            • Épanchements pleuraux

            Symptômes courants:
            • Toux et fièvre
            • Difficultés respiratoires
            • Douleur thoracique
            """)

    def afficher_upload_section(self):
        """Affiche la section de téléchargement d'image"""
        st.markdown("### 📤 Télécharger une Radiographie")
        
        with st.container():
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Choisissez une image de radiographie pulmonaire",
                type=['jpg', 'jpeg', 'png'],
                help="Formats supportés: JPEG, PNG",
                key="file_uploader"
            )
            
            if uploaded_file is not None:
                try:
                    # Afficher l'image
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Radiographie téléchargée", use_column_width=True)
                    
                    # Stocker l'image dans la session
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format='JPEG')
                    st.session_state.current_image = img_bytes.getvalue()
                    st.session_state.image_uploaded = True
                    
                    st.success("✅ Image téléchargée avec succès! Posez votre question dans le chat.")
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors du chargement de l'image: {e}")
            else:
                st.session_state.current_image = None
                st.session_state.image_uploaded = False
            
            st.markdown('</div>', unsafe_allow_html=True)

    def _analyser_image_avec_serveur(self, image_bytes: bytes) -> str:
        """Envoie l'image au serveur pour analyse"""
        try:
            files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
            response = requests.post("http://localhost:8000/predict", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'success':
                    return f"""
📊 RÉSULTAT DE L'ANALYSE

🎯 Diagnostic: {result['prediction']}
📈 Niveau de confiance: {result['confidence']:.1%}

📋 Détails:
- Probabilité NORMAL: {result['probabilities']['NORMAL']:.1%}
- Probabilité PNEUMONIA: {result['probabilities']['PNEUMONIA']:.1%}

💡 Explication:
{'L\'analyse ne détecte pas de signes évidents de pneumonie sur cette radiographie.' 
 if result['prediction'] == 'NORMAL' 
 else 'L\'analyse détecte des signes évocateurs de pneumonie.'}

⚠ AVERTISSEMENT MÉDICAL IMPORTANT
Ce résultat est fourni par une intelligence artificielle et ne remplace pas un diagnostic médical professionnel. 
Consultez toujours un médecin qualifié pour toute décision médicale.
"""
                else:
                    return f"❌ Erreur lors de l'analyse: {result.get('error', 'Erreur inconnue')}"
            else:
                return f"❌ Erreur serveur: {response.status_code}"
                
        except Exception as e:
            return f"❌ Erreur de connexion au serveur: {str(e)}"

    def _repondre_question_generale(self, question: str) -> str:
        """Répond aux questions générales"""
        # Pour l'instant, réponses prédéfinies - vous pourrez intégrer GPT-4 ici
        faqs = {
            "symptômes pneumonie": """
🤒 Symptômes courants de la pneumonie:

• Toux (sèche ou productive)
• Fièvre et frissons
• Difficultés respiratoires
• Douleur thoracique
• Fatigue importante
• Transpiration excessive

🩺 Quand consulter:
Consultez un médecin si vous présentez ces symptômes, surtout si vous avez des difficultés respiratoires.
""",
            "causes pneumonie": """
🦠 Causes principales de la pneumonie:

• Bactéries (Streptococcus pneumoniae)
• Virus (grippe, COVID-19, VRS)
• Champignons (plus rare)
• Aspiration de liquides ou aliments

🎯 Facteurs de risque:
Âge avancé, système immunitaire affaibli, tabagisme, maladies chroniques.
""",
            "traitement pneumonie": """
💊 Traitements possibles:

• Antibiotiques pour les pneumonies bactériennes
• Antiviraux pour les pneumonies virales
• Repos et hydratation
• Médicaments contre la fièvre et la douleur
• Oxygénothérapie si nécessaire

📞 Important: Le traitement doit être prescrit par un médecin.
""",
            "prévention pneumonie": """
🛡 Mesures préventives:

• Vaccination (grippe, pneumocoque)
• Hygiène des mains régulière
• Éviter le tabagisme
• Alimentation équilibrée
• Exercice physique régulier
"""
        }
        
        question_lower = question.lower()
        for key, response in faqs.items():
            if key in question_lower:
                return response
        
        # Réponse par défaut
        return """
Je suis spécialisé dans l'analyse des radiographies pulmonaires. 

Pour des questions médicales spécifiques, je vous recommande de:
• Consulter un médecin généraliste
• Visiter un service d'urgences en cas de symptômes graves
• Contacter un pneumologue pour des problèmes pulmonaires

📞 En cas d'urgence: Appelez le 15 (SAMU)
"""

    def afficher_chat(self):
        """Affiche l'interface de chat unifiée"""
        st.markdown("### 💬 Dialogue avec MediBot")
        
        # Affichage de l'historique des messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-user"><strong>👤 Vous:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot"><strong>🤖 MediBot:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)

        # Input utilisateur
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input(
                "Votre message...",
                placeholder="Posez une question ou discutez de la radiographie téléchargée...",
                key="user_input"
            )
        with col2:
            send_button = st.button("📤 Envoyer", use_container_width=True)

        # Gestion de l'envoi du message
        if send_button and user_input:
            # Ajouter le message utilisateur à l'historique
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Réponse de l'assistant
            with st.spinner("🤖 MediBot réfléchit..."):
                try:
                    # Utiliser l'image si disponible, sinon question générale
                    image_bytes = st.session_state.get('current_image')
                    if image_bytes:
                        response = self._analyser_image_avec_serveur(image_bytes)
                    else:
                        response = self._repondre_question_generale(user_input)
                    
                    # Ajouter la réponse à l'historique
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # Rafraîchir l'interface
                    st.rerun()
                    
                except Exception as e:
                    error_msg = f"❌ Erreur: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    st.rerun()

    def afficher_guide_rapide(self):
        """Affiche un guide rapide des questions possibles"""
        with st.expander("📋 Questions rapides (cliquez pour copier)"):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🤒 Symptômes pneumonie"):
                    st.session_state.user_input = "Quels sont les symptômes de la pneumonie ?"
                    st.rerun()
                
                if st.button("🦠 Causes pneumonie"):
                    st.session_state.user_input = "Quelles sont les causes de la pneumonie ?"
                    st.rerun()
            
            with col2:
                if st.button("💊 Traitements"):
                    st.session_state.user_input = "Comment traite-t-on la pneumonie ?"
                    st.rerun()
                
                if st.button("🛡 Prévention"):
                    st.session_state.user_input = "Comment prévenir la pneumonie ?"
                    st.rerun()

    def lancer_interface(self):
        """Lance l'interface principale unifiée"""
        self.afficher_entete()
        self.afficher_avertissement()
        self.afficher_sidebar()
        
        # Interface principale en deux colonnes
        col1, col2 = st.columns([1, 1])
        
        with col1:
            self.afficher_upload_section()
            self.afficher_guide_rapide()
        
        with col2:
            self.afficher_chat()

def main():
    """Fonction principale"""
    interface = InterfaceMediBot()
    interface.lancer_interface()

if __name__ == "__main__":
    main()