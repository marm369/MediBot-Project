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
            page_title="PneumoScan AI - Assistant Médical",
            page_icon="🫁",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # CSS Moderne inspiré des designs médicaux professionnels
        st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* ========== VARIABLES ========== */
        :root {
            --primary: #2b8cee;
            --primary-hover: #2374cc;
            --bg-light: #f6f7f8;
            --bg-dark: #101922;
            --surface-light: #ffffff;
            --surface-dark: #1a2632;
            --text-light: #111418;
            --text-dark: #ffffff;
            --text-secondary-light: #617589;
            --text-secondary-dark: #9dabb9;
            --border-light: #f0f2f4;
            --border-dark: #283039;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.15);
            --shadow-lg: 0 8px 24px rgba(0,0,0,0.2);
        }
        
        /* ========== GLOBAL ========== */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .stApp {
            background: var(--bg-light);
            color: var(--text-light);
        }
        
        /* Mode sombre */
        [data-theme="dark"] .stApp {
            background: var(--bg-dark);
            color: var(--text-dark);
        }
        
        /* ========== SCROLLBAR ========== */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        [data-theme="dark"] ::-webkit-scrollbar-thumb {
            background: #334155;
        }
        
        /* ========== HEADER ========== */
        .main-header {
            text-align: left;
            padding: 1.5rem 0;
            border-bottom: 1px solid var(--border-light);
            margin-bottom: 1rem;
            background: var(--surface-light);
        }
        
        [data-theme="dark"] .main-header {
            border-color: var(--border-dark);
            background: var(--surface-dark);
        }
        
        .header-title {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-light);
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin: 0;
        }
        
        [data-theme="dark"] .header-title {
            color: var(--text-dark);
        }
        
        .header-subtitle {
            font-size: 0.75rem;
            color: var(--text-secondary-light);
            margin-top: 0.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        [data-theme="dark"] .header-subtitle {
            color: var(--text-secondary-dark);
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            display: inline-block;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* ========== DISCLAIMER ========== */
        .disclaimer {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left: 3px solid var(--warning);
            border-radius: 8px;
            padding: 0.875rem 1rem;
            margin: 1rem 0;
            display: flex;
            align-items: start;
            gap: 0.75rem;
            box-shadow: var(--shadow-sm);
        }
        
        [data-theme="dark"] .disclaimer {
            background: rgba(245, 158, 11, 0.15);
            border-color: var(--warning);
        }
        
        .disclaimer-icon {
            color: #92400e;
            font-size: 1.25rem;
            flex-shrink: 0;
        }
        
        [data-theme="dark"] .disclaimer-icon {
            color: var(--warning);
        }
        
        .disclaimer-text {
            font-size: 0.8rem;
            color: #78350f;
            line-height: 1.5;
        }
        
        [data-theme="dark"] .disclaimer-text {
            color: #fde68a;
        }
        
        /* ========== MESSAGES CHAT ========== */
        .chat-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 1rem 0;
        }
        
        .message-wrapper {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message-wrapper.user {
            flex-direction: row-reverse;
        }
        
        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;
            box-shadow: var(--shadow-sm);
        }
        
        .avatar.bot {
            background: linear-gradient(135deg, var(--primary) 0%, #1e40af 100%);
            color: white;
        }
        
        .avatar.user {
            background: #64748b;
            color: white;
        }
        
        .message-content {
            flex: 1;
            max-width: 75%;
        }
        
        .message-header {
            display: flex;
            align-items: baseline;
            gap: 0.5rem;
            margin-bottom: 0.25rem;
        }
        
        .message-wrapper.user .message-header {
            flex-direction: row-reverse;
        }
        
        .message-author {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-light);
        }
        
        [data-theme="dark"] .message-author {
            color: var(--text-dark);
        }
        
        .message-time {
            font-size: 0.65rem;
            color: var(--text-secondary-light);
        }
        
        [data-theme="dark"] .message-time {
            color: var(--text-secondary-dark);
        }
        
        .message-bubble {
            padding: 1rem 1.25rem;
            border-radius: 16px;
            font-size: 0.9rem;
            line-height: 1.6;
            box-shadow: var(--shadow-sm);
            word-wrap: break-word;
        }
        
        .message-bubble.bot {
            background: var(--surface-light);
            border: 1px solid var(--border-light);
            border-top-left-radius: 4px;
            color: var(--text-light);
        }
        
        [data-theme="dark"] .message-bubble.bot {
            background: var(--surface-dark);
            border-color: var(--border-dark);
            color: var(--text-dark);
        }
        
        .message-bubble.user {
            background: linear-gradient(135deg, var(--primary) 0%, #1e40af 100%);
            border-top-right-radius: 4px;
            color: white;
        }
        
        .image-preview {
            background: rgba(0,0,0,0.05);
            padding: 0.5rem;
            border-radius: 8px;
            margin-top: 0.75rem;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.8rem;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        [data-theme="dark"] .image-preview {
            background: rgba(255,255,255,0.1);
        }
        
        /* ========== QUICK ACTIONS ========== */
        .quick-actions {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-bottom: 1rem;
        }
        
        .quick-btn {
            background: var(--surface-light);
            border: 1px solid var(--border-light);
            color: var(--text-light);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        [data-theme="dark"] .quick-btn {
            background: var(--surface-dark);
            border-color: var(--border-dark);
            color: var(--text-dark);
        }
        
        .quick-btn:hover {
            background: var(--primary);
            color: white;
            border-color: var(--primary);
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        /* ========== IMAGE BADGE ========== */
        .image-badge-container {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }
        
        .image-badge {
            background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: var(--shadow-sm);
        }
        
        /* ========== INPUT AREA ========== */
        .input-container {
            position: sticky;
            bottom: 0;
            background: var(--surface-light);
            border-top: 1px solid var(--border-light);
            padding: 1rem;
            box-shadow: 0 -4px 12px rgba(0,0,0,0.05);
        }
        
        [data-theme="dark"] .input-container {
            background: var(--surface-dark);
            border-color: var(--border-dark);
        }
        
        .stTextArea textarea {
            background: var(--bg-light) !important;
            border: 1px solid var(--border-light) !important;
            border-radius: 12px !important;
            color: var(--text-light) !important;
            font-size: 0.9rem !important;
            transition: all 0.2s !important;
        }
        
        [data-theme="dark"] .stTextArea textarea {
            background: #151f28 !important;
            border-color: var(--border-dark) !important;
            color: var(--text-dark) !important;
        }
        
        .stTextArea textarea:focus {
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(43, 140, 238, 0.1) !important;
        }
        
        .stButton button {
            background: linear-gradient(135deg, var(--primary) 0%, #1e40af 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.625rem 1.5rem !important;
            transition: all 0.2s !important;
            box-shadow: 0 2px 8px rgba(43, 140, 238, 0.3) !important;
        }
        
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 16px rgba(43, 140, 238, 0.4) !important;
        }
        
        /* Boutons secondaires */
        .stButton button[kind="secondary"] {
            background: transparent !important;
            border: 1px solid var(--border-light) !important;
            color: var(--text-light) !important;
            box-shadow: none !important;
        }
        
        [data-theme="dark"] .stButton button[kind="secondary"] {
            border-color: var(--border-dark) !important;
            color: var(--text-dark) !important;
        }
        
        /* ========== SIDEBAR ========== */
        section[data-testid="stSidebar"] {
            background: var(--surface-light) !important;
            border-right: 1px solid var(--border-light) !important;
        }
        
        [data-theme="dark"] section[data-testid="stSidebar"] {
            background: #111418 !important;
            border-right-color: var(--border-dark) !important;
        }
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {
            color: var(--text-light);
        }
        
        [data-theme="dark"] section[data-testid="stSidebar"] h1,
        [data-theme="dark"] section[data-testid="stSidebar"] h2,
        [data-theme="dark"] section[data-testid="stSidebar"] h3 {
            color: var(--text-dark);
        }
        
        /* ========== EXPANDER ========== */
        .streamlit-expanderHeader {
            background: var(--bg-light) !important;
            border: 1px solid var(--border-light) !important;
            border-radius: 8px !important;
            color: var(--text-light) !important;
            font-weight: 500 !important;
        }
        
        [data-theme="dark"] .streamlit-expanderHeader {
            background: rgba(255,255,255,0.03) !important;
            border-color: var(--border-dark) !important;
            color: var(--text-dark) !important;
        }
        
        /* ========== RESPONSIVE ========== */
        @media (max-width: 768px) {
            .message-content {
                max-width: 85%;
            }
            
            .header-title {
                font-size: 1.5rem;
            }
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
        if "dark_mode" not in st.session_state:
            st.session_state.dark_mode = True

    def _initialiser_assistant(self):
        """Initialise l'assistant médical GPT"""
        if "assistant" not in st.session_state:
            st.session_state.assistant = AssistantMedicalGPT()

    def afficher_entete(self):
        """Affiche l'en-tête de l'application"""
        theme_attr = 'dark' if st.session_state.dark_mode else 'light'
        st.markdown(f"""
        <script>
        document.querySelector('.stApp').setAttribute('data-theme', '{theme_attr}');
        </script>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="main-header">
            <div class="header-title">
                🫁 PneumoScan AI
            </div>
            <div class="header-subtitle">
                <span class="status-dot"></span>
                Assistant Médical Intelligent · Analyse de Pneumonie
            </div>
        </div>
        """, unsafe_allow_html=True)

    def afficher_avertissement(self):
        """Affiche l'avertissement médical"""
        st.markdown("""
        <div class="disclaimer">
            <div class="disclaimer-icon">⚠️</div>
            <div class="disclaimer-text">
                <strong>Avertissement médical:</strong> Cet outil est destiné à l'assistance uniquement. 
                Vérifiez toujours les informations avec un professionnel de santé. 
                <strong>Urgence: appelez le 15 (SAMU).</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def afficher_sidebar(self):
        """Affiche la barre latérale"""
        with st.sidebar:
            # Toggle mode sombre/clair
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("### 🔧 Paramètres")
            with col2:
                if st.button("🌓", key="theme_toggle"):
                    st.session_state.dark_mode = not st.session_state.dark_mode
                    st.rerun()
            
            st.markdown("---")
            
            st.markdown("### 📊 État du Système")
            
            # Vérifier GPT-4
            if st.session_state.assistant.use_gpt4:
                st.success("✅ GPT-4 connecté")
            else:
                st.error("❌ GPT-4 non configuré")
                with st.expander("📖 Configuration"):
                    st.markdown("""
                    1. Obtenez une clé API sur [OpenAI](https://platform.openai.com/)
                    2. Créez `.env` à la racine
                    3. Ajoutez: `OPENAI_API_KEY=votre_cle`
                    4. Redémarrez
                    """)
            
            # Vérifier le serveur
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    st.success("✅ Serveur de classification")
                else:
                    st.error("❌ Serveur hors ligne")
            except:
                st.error("❌ Serveur non accessible")
                st.info("Démarrez: `python serveur_medical.py`")

            st.markdown("---")
            
            # Bouton nouvelle conversation
            if st.button("🔄 Nouvelle conversation", use_container_width=True, type="primary"):
                st.session_state.messages = []
                st.session_state.conversation_history = []
                st.session_state.current_image = None
                st.session_state.image_name = None
                st.session_state.assistant.reset_conversation()
                st.rerun()

            st.markdown("---")
            st.markdown("### 💡 Guide")
            
            with st.expander("📋 Comment utiliser", expanded=True):
                st.markdown("""
                **Questions naturelles:**
                - Symptômes de la pneumonie
                - Traitements disponibles
                - Prévention et conseils
                
                **Analyse de radiographie:**
                1. Joindre une image
                2. Poser une question
                3. Recevoir l'analyse
                """)

            st.markdown("---")
            st.metric("Messages échangés", len(st.session_state.messages))
            
            if st.session_state.current_image:
                st.info("📸 Image attachée")

    def afficher_attacher_image(self):
        """Zone pour attacher une image"""
        with st.expander("📎 Joindre une radiographie", expanded=False):
            uploaded_file = st.file_uploader(
                "Image JPG/PNG",
                type=['jpg', 'jpeg', 'png'],
                help="Sera analysée automatiquement",
                key="file_uploader"
            )
            
            if uploaded_file is not None:
                try:
                    image = Image.open(uploaded_file)
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.image(image, use_container_width=True)
                    with col2:
                        st.success(f"✅ {uploaded_file.name}")
                        st.info("💡 Prêt pour analyse")
                    
                    img_bytes = io.BytesIO()
                    image.save(img_bytes, format='JPEG')
                    st.session_state.current_image = img_bytes.getvalue()
                    st.session_state.image_name = uploaded_file.name
                    
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
            else:
                if st.session_state.current_image:
                    st.info(f"📸 {st.session_state.image_name}")
                    if st.button("🗑️ Retirer"):
                        st.session_state.current_image = None
                        st.session_state.image_name = None
                        st.rerun()

    def afficher_chat(self):
        """Affiche l'interface de chat"""
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Afficher l'historique
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                st.markdown(f"""
                <div class="message-wrapper user">
                    <div class="avatar user">👤</div>
                    <div class="message-content">
                        <div class="message-header">
                            <span class="message-author">Vous</span>
                            <span class="message-time">maintenant</span>
                        </div>
                        <div class="message-bubble user">
                            {message["content"]}
                            {f'<div class="image-preview">📸 {message.get("image_name", "image.jpg")}</div>' if message.get("has_image") else ""}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-wrapper bot">
                    <div class="avatar bot">🤖</div>
                    <div class="message-content">
                        <div class="message-header">
                            <span class="message-author">Dr. IA</span>
                            <span class="message-time">maintenant</span>
                        </div>
                        <div class="message-bubble bot">
                            {message["content"]}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Zone de saisie
        st.markdown("---")
        
        # Questions rapides
        st.markdown("**💡 Questions rapides:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🤒 Symptômes", key="q1", use_container_width=True):
                self._envoyer_question_rapide("Quels sont les symptômes de la pneumonie ?")
        with col2:
            if st.button("🦠 Causes", key="q2", use_container_width=True):
                self._envoyer_question_rapide("Quelles sont les causes de la pneumonie ?")
        with col3:
            if st.button("💊 Traitements", key="q3", use_container_width=True):
                self._envoyer_question_rapide("Comment traite-t-on la pneumonie ?")
        with col4:
            if st.button("🛡️ Prévention", key="q4", use_container_width=True):
                self._envoyer_question_rapide("Comment prévenir la pneumonie ?")
        
        # Badge image + retirer
        if st.session_state.current_image:
            col_badge, col_btn = st.columns([3, 1])
            with col_badge:
                st.markdown(f'<div class="image-badge">📸 {st.session_state.image_name}</div>', unsafe_allow_html=True)
            with col_btn:
                if st.button("🗑️ Retirer", key="remove_img"):
                    st.session_state.current_image = None
                    st.session_state.image_name = None
                    st.rerun()
        
        # Input
        user_input = st.text_area(
            "Votre message:",
            placeholder="Posez votre question sur la pneumonie, les symptômes, ou uploadez une radiographie...",
            height=100,
            key="user_input"
        )
        
        col1, col2 = st.columns([4, 1])
        with col1:
            send = st.button("📤 Envoyer", type="primary", use_container_width=True)
        
        if send and user_input.strip():
            self._traiter_message(user_input)

    def _envoyer_question_rapide(self, question: str):
        """Envoie une question rapide"""
        self._traiter_message(question)

    def _traiter_message(self, user_input: str):
        """Traite le message"""
        message_user = {
            "role": "user",
            "content": user_input,
            "has_image": st.session_state.current_image is not None,
            "image_name": st.session_state.image_name
        }
        st.session_state.messages.append(message_user)
        
        st.session_state.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        with st.spinner("🤖 Réflexion..."):
            try:
                response = st.session_state.assistant.chat(
                    message_utilisateur=user_input,
                    image_bytes=st.session_state.current_image,
                    conversation_history=st.session_state.conversation_history[:-1]
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                
                if st.session_state.current_image:
                    st.session_state.current_image = None
                    st.session_state.image_name = None
                
                st.rerun()
                
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ Erreur: {str(e)}"
                })
                st.rerun()

    def lancer_interface(self):
        """Lance l'interface"""
        self.afficher_entete()
        self.afficher_avertissement()
        self.afficher_sidebar()
        self.afficher_attacher_image()
        self.afficher_chat()

def main():
    interface = InterfaceMediBot()
    interface.lancer_interface()

if __name__ == "__main__":
    main()