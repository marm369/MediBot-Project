import streamlit as st
import os
import sys
from PIL import Image
import io
import logging
import requests

# Ajouter le chemin pour importer assistant_medical depuis le dossier chatbot
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
chatbot_dir = os.path.join(parent_dir, 'chatbot')
sys.path.insert(0, chatbot_dir)
sys.path.insert(0, parent_dir)

try:
    from assistant_medical import AssistantMedicalGPT
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "assistant_medical",
        os.path.join(chatbot_dir, "assistant_medical.py")
    )
    assistant_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assistant_module)
    AssistantMedicalGPT = assistant_module.AssistantMedicalGPT

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InterfaceMediBot:
    def __init__(self):
        self._initialiser_page()
        self._initialiser_session()
        self._initialiser_assistant()

    def _initialiser_page(self):
        """Configure la page Streamlit"""
        st.set_page_config(
            page_title="MediBot - Assistant Médical IA Conversationnel",
            page_icon="🏥",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # CSS personnalisé moderne avec animations
        st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Variables CSS */
        :root {
            --primary-color: #2563eb;
            --secondary-color: #10b981;
            --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --shadow-sm: 0 2px 8px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 16px rgba(0,0,0,0.15);
            --shadow-lg: 0 8px 32px rgba(0,0,0,0.2);
        }
        
        /* Style global */
        .stApp {
            font-family: 'Inter', sans-serif;
        }
        
        /* Header avec gradient animé */
        .main-header {
            font-size: 2.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            background-size: 200% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 1.5rem;
            animation: gradientShift 8s ease infinite;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        /* Subtitle animé */
        .subtitle {
            text-align: center;
            color: #6b7280;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            animation: fadeInUp 0.8s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Warning box modernisé */
        .warning-box {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left: 4px solid #f59e0b;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: var(--shadow-sm);
            animation: fadeIn 0.6s ease-out;
        }
        
        .warning-box h4 {
            color: #92400e;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .warning-box p {
            color: #78350f;
            margin: 0.5rem 0;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Messages chat avec animations */
        .chat-message {
            animation: slideIn 0.4s ease-out;
            margin: 1rem 0;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .chat-user {
            background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
            padding: 1.2rem;
            border-radius: 16px;
            border-left: 4px solid #3b82f6;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
        }
        
        .chat-user:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .chat-bot {
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            padding: 1.2rem;
            border-radius: 16px;
            border-left: 4px solid #10b981;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
        }
        
        .chat-bot:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .message-header {
            font-weight: 600;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .message-content {
            color: #1f2937;
            line-height: 1.6;
        }
        
        /* Image attachée */
        .image-attached {
            background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
            padding: 0.75rem;
            border-radius: 10px;
            font-size: 0.9rem;
            margin-top: 0.75rem;
            border: 2px solid #6ee7b7;
            display: inline-block;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.8; }
        }
        
        /* Boutons de questions rapides */
        .quick-question-btn {
            transition: all 0.3s ease;
        }
        
        .quick-question-btn:hover {
            transform: translateY(-3px);
            box-shadow: var(--shadow-md);
        }
        
        /* Zone d'input modernisée */
        .stTextArea textarea {
            border-radius: 12px !important;
            border: 2px solid #e5e7eb !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextArea textarea:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        }
        
        /* Boutons */
        .stButton button {
            border-radius: 10px !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
            border: none !important;
        }
        
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md) !important;
        }
        
        /* Badge d'image attachée */
        .image-badge {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            display: inline-block;
            box-shadow: var(--shadow-sm);
            animation: bounceIn 0.5s ease-out;
        }
        
        @keyframes bounceIn {
            0% {
                opacity: 0;
                transform: scale(0.3);
            }
            50% {
                opacity: 1;
                transform: scale(1.05);
            }
            100% {
                transform: scale(1);
            }
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%) !important;
            border-radius: 10px !important;
            font-weight: 500 !important;
        }
        
        /* Scrollbar personnalisée */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        </style>
        """, unsafe_allow_html=True)

    def _initialiser_session(self):
        """Initialise les variables de session"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_image" not in st.session_state:
            st.session_state.current_image = None
        if "image_name" not in st.session_state:
            st.session_state.image_name = None
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

    def _initialiser_assistant(self):
        """Initialise l'assistant médical GPT"""
        if "assistant" not in st.session_state:
            st.session_state.assistant = AssistantMedicalGPT()

    def afficher_entete(self):
        """Affiche l'en-tête de l'application"""
        st.markdown('<h1 class="main-header">🏥 MediBot - Assistant Médical IA</h1>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="subtitle">
            💬 <strong>Chatbot conversationnel intelligent</strong><br>
            Posez vos questions sur la pneumonie et les maladies pulmonaires<br>
            📸 Attachez une radiographie pour analyse automatique
        </div>
        """, unsafe_allow_html=True)

    def afficher_avertissement(self):
        """Affiche l'avertissement médical"""
        st.markdown("""
        <div class="warning-box">
        <h4>⚠️ AVERTISSEMENT MÉDICAL IMPORTANT</h4>
        <p>Ce chatbot est un <strong>outil d'information et d'aide à la décision</strong>. Il ne remplace en aucun cas un diagnostic médical professionnel.</p>
        <p><strong>Consultez toujours un médecin qualifié</strong> pour toute décision médicale.</p>
        <p><strong>🚨 Urgence médicale: appelez le 15 (SAMU) immédiatement</strong></p>
        </div>
        """, unsafe_allow_html=True)

    def afficher_sidebar(self):
        """Affiche la barre latérale"""
        with st.sidebar:
            st.header("🔧 État du Système")
            
            # Vérifier GPT-4
            if st.session_state.assistant.use_gpt4:
                st.success("✅ GPT-4 connecté")
            else:
                st.error("❌ GPT-4 non configuré")
                with st.expander("📖 Comment configurer GPT-4"):
                    st.markdown("""
                    1. Obtenez une clé API sur [OpenAI](https://platform.openai.com/)
                    2. Créez un fichier `.env` à la racine
                    3. Ajoutez: `OPENAI_API_KEY=votre_cle_ici`
                    4. Redémarrez l'application
                    """)
            
            # Vérifier le serveur de classification
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    st.success("✅ Serveur de classification connecté")
                else:
                    st.error("❌ Serveur de classification hors ligne")
            except:
                st.error("❌ Serveur non accessible")
                st.info("Démarrez-le avec: `python serveur_medical.py`")

            st.markdown("---")
            
            # Bouton pour réinitialiser la conversation
            if st.button("🔄 Nouvelle conversation", use_container_width=True):
                st.session_state.messages = []
                st.session_state.conversation_history = []
                st.session_state.current_image = None
                st.session_state.image_name = None
                st.session_state.assistant.reset_conversation()
                st.rerun()

            st.markdown("---")
            st.header("💡 Guide d'utilisation")
            
            st.markdown("""
            **💬 Conversation naturelle:**
            - Posez n'importe quelle question sur la pneumonie
            - Demandez des explications sur les symptômes
            - Renseignez-vous sur les traitements
            - Discutez de prévention
            
            **📸 Analyse de radiographie:**
            1. Cliquez sur "📎 Joindre une radiographie"
            2. Sélectionnez votre image
            3. Posez votre question dans le chat
            4. L'image sera analysée automatiquement
            
            **Exemples de questions:**
            - "Quels sont les symptômes de la pneumonie ?"
            - "Comment se transmet cette maladie ?"
            - "Analysez cette radiographie s'il vous plaît"
            - "Que signifie ce résultat ?"
            """)

            st.markdown("---")
            st.header("📊 Statistiques")
            st.metric("Messages échangés", len(st.session_state.messages))
            if st.session_state.current_image:
                st.info("📸 Image attachée prête pour analyse")

    def afficher_attacher_image(self):
        """Zone pour attacher une image à la conversation"""
        with st.expander("📎 Joindre une radiographie (optionnel)", expanded=False):
            uploaded_file = st.file_uploader(
                "Sélectionnez une radiographie pulmonaire",
                type=['jpg', 'jpeg', 'png'],
                help="L'image sera analysée lors de votre prochain message",
                key="file_uploader"
            )
            
            if uploaded_file is not None:
                try:
                    # Afficher l'image en petit
                    image = Image.open(uploaded_file)
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(image, caption="Image attachée", use_container_width=True)
                    with col2:
                        st.success(f"✅ **{uploaded_file.name}** prêt pour analyse")
                        st.info("💡 Posez votre question dans le chat ci-dessous. L'image sera analysée automatiquement.")
                    
                    # Stocker l'image
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format='JPEG')
                    st.session_state.current_image = img_bytes.getvalue()
                    st.session_state.image_name = uploaded_file.name
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors du chargement: {e}")
            else:
                if st.session_state.current_image:
                    st.info(f"📸 Image actuelle: {st.session_state.image_name}")
                    if st.button("🗑️ Retirer l'image"):
                        st.session_state.current_image = None
                        st.session_state.image_name = None
                        st.rerun()

    def afficher_chat(self):
        """Affiche l'interface de chat conversationnel"""
        st.markdown("### 💬 Conversation")
        
        # Conteneur pour les messages avec scroll
        chat_container = st.container()
        
        with chat_container:
            # Afficher l'historique
            for i, message in enumerate(st.session_state.messages):
                if message["role"] == "user":
                    st.markdown(f'<div class="chat-message">', unsafe_allow_html=True)
                    st.markdown(f'<div class="chat-user">', unsafe_allow_html=True)
                    st.markdown(f'<div class="message-header">👤 Vous</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="message-content">{message["content"]}</div>', unsafe_allow_html=True)
                    if message.get("has_image"):
                        st.markdown(f'<div class="image-attached">📸 Image: {message.get("image_name", "radiographie.jpg")}</div>', unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message">', unsafe_allow_html=True)
                    st.markdown(f'<div class="chat-bot">', unsafe_allow_html=True)
                    st.markdown(f'<div class="message-header">🤖 Dr. IA</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="message-content">{message["content"]}</div>', unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)
        
        # Zone de saisie
        st.markdown("---")
        
        # Exemples rapides AVEC CALLBACK
        st.markdown("**💡 Questions rapides:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🤒 Symptômes", use_container_width=True, key="btn_symptomes"):
                self._envoyer_question_rapide("Quels sont les symptômes de la pneumonie ?")
        with col2:
            if st.button("🦠 Causes", use_container_width=True, key="btn_causes"):
                self._envoyer_question_rapide("Quelles sont les causes de la pneumonie ?")
        with col3:
            if st.button("💊 Traitements", use_container_width=True, key="btn_traitements"):
                self._envoyer_question_rapide("Comment traite-t-on la pneumonie ?")
        with col4:
            if st.button("🛡️ Prévention", use_container_width=True, key="btn_prevention"):
                self._envoyer_question_rapide("Comment prévenir la pneumonie ?")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Badge d'image si présente + bouton retirer
        if st.session_state.current_image:
            col_badge, col_remove = st.columns([3, 1])
            with col_badge:
                st.markdown(f'<div class="image-badge">📸 {st.session_state.image_name}</div>', unsafe_allow_html=True)
            with col_remove:
                if st.button("🗑️ Retirer", key="remove_image_bottom"):
                    st.session_state.current_image = None
                    st.session_state.image_name = None
                    st.rerun()
        
        # Input utilisateur
        user_input = st.text_area(
            "Votre message:",
            placeholder="Posez votre question sur la pneumonie, les symptômes, les traitements...\nSi vous avez attaché une image, elle sera analysée automatiquement.",
            height=100,
            key="user_input_area"
        )
        
        col1, col2 = st.columns([4, 1])
        with col1:
            send_button = st.button("📤 Envoyer", use_container_width=True, type="primary")

        # Traitement de l'envoi
        if send_button and user_input.strip():
            self._traiter_message(user_input)

    def _envoyer_question_rapide(self, question: str):
        """Envoie directement une question rapide"""
        self._traiter_message(question)

    def _traiter_message(self, user_input: str):
        """Traite le message de l'utilisateur"""
        # Ajouter le message utilisateur
        message_user = {
            "role": "user",
            "content": user_input,
            "has_image": st.session_state.current_image is not None,
            "image_name": st.session_state.image_name
        }
        st.session_state.messages.append(message_user)
        
        # Ajouter à l'historique pour GPT
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Générer la réponse
        with st.spinner("🤖 Dr. IA réfléchit..."):
            try:
                # Appeler l'assistant avec ou sans image
                response = st.session_state.assistant.chat(
                    message_utilisateur=user_input,
                    image_bytes=st.session_state.current_image,
                    conversation_history=st.session_state.conversation_history[:-1]
                )
                
                # Ajouter la réponse
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
                # Ajouter à l'historique GPT
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                # Réinitialiser l'image après utilisation
                if st.session_state.current_image:
                    st.session_state.current_image = None
                    st.session_state.image_name = None
                
                # Rafraîchir
                st.rerun()
                
            except Exception as e:
                error_msg = f"❌ Erreur: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.rerun()

    def lancer_interface(self):
        """Lance l'interface principale"""
        self.afficher_entete()
        self.afficher_avertissement()
        self.afficher_sidebar()
        
        # Interface principale
        self.afficher_attacher_image()
        self.afficher_chat()

def main():
    """Fonction principale"""
    interface = InterfaceMediBot()
    interface.lancer_interface()

if __name__ == "__main__":
    main()