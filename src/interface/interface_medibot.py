import streamlit as st
import os
import sys
from PIL import Image
import io
import logging
import requests
import re

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
            st.session_state.dark_mode = False
        if "theme_initialized" not in st.session_state:
            st.session_state.theme_initialized = False

    def _initialiser_assistant(self):
        """Initialise l'assistant médical GPT"""
        if "assistant" not in st.session_state:
            st.session_state.assistant = AssistantMedicalGPT()

    def _appliquer_css(self):
        """Applique le CSS dynamiquement selon le thème"""
        theme = "dark" if st.session_state.dark_mode else "light"
        
        css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* ========== GLOBAL ========== */
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* ========== THÈME DYNAMIQUE ========== */
        .stApp {{
            background: {"#101922" if theme == "dark" else "#f6f7f8"} !important;
            color: {"#ffffff" if theme == "dark" else "#111418"} !important;
            transition: background 0.3s ease, color 0.3s ease;
        }}
        
        /* ========== SCROLLBAR ========== */
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: transparent;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {"#334155" if theme == "dark" else "#cbd5e1"};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {"#475569" if theme == "dark" else "#94a3b8"};
        }}
        
        /* ========== HEADER AMÉLIORÉ ========== */
        .modern-header {{
            background: linear-gradient(135deg, #2b8cee 0%, #1e40af 100%);
            padding: 2rem 1.5rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(43, 140, 238, 0.25);
        }}
        
        .header-title {{
            font-size: 2rem;
            font-weight: 700;
            color: white;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        
        .header-subtitle {{
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.9);
            margin-top: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .status-dot {{
            width: 10px;
            height: 10px;
            background: #10b981;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 2s infinite;
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.6);
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.7; transform: scale(0.95); }}
        }}
        
        /* ========== DISCLAIMER ========== */
        .disclaimer {{
            background: {"rgba(245, 158, 11, 0.15)" if theme == "dark" else "linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)"};
            border-left: 4px solid #f59e0b;
            border-radius: 12px;
            padding: 1rem 1.25rem;
            margin: 1.5rem 0;
            display: flex;
            align-items: start;
            gap: 1rem;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.15);
        }}
        
        .disclaimer-icon {{
            font-size: 1.5rem;
            flex-shrink: 0;
        }}
        
        .disclaimer-text {{
            font-size: 0.85rem;
            color: {"#fde68a" if theme == "dark" else "#78350f"};
            line-height: 1.6;
        }}
        
        /* ========== MESSAGES CHAT ========== */
        .chat-container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 1rem 0 2rem 0;
        }}
        
        .message-wrapper {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            animation: slideIn 0.4s ease-out;
        }}
        
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(15px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .message-wrapper.user {{
            flex-direction: row-reverse;
        }}
        
        .avatar {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            flex-shrink: 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        }}
        
        .avatar.bot {{
            background: linear-gradient(135deg, #2b8cee 0%, #1e40af 100%);
        }}
        
        .avatar.user {{
            background: linear-gradient(135deg, #64748b 0%, #475569 100%);
        }}
        
        .message-content {{
            flex: 1;
            max-width: 75%;
        }}
        
        .message-header {{
            display: flex;
            align-items: baseline;
            gap: 0.5rem;
            margin-bottom: 0.4rem;
        }}
        
        .message-wrapper.user .message-header {{
            flex-direction: row-reverse;
        }}
        
        .message-author {{
            font-size: 0.9rem;
            font-weight: 600;
            color: {"#ffffff" if theme == "dark" else "#111418"};
        }}
        
        .message-time {{
            font-size: 0.7rem;
            color: {"#9dabb9" if theme == "dark" else "#617589"};
        }}
        
        .message-bubble {{
            padding: 1rem 1.25rem;
            border-radius: 18px;
            font-size: 0.95rem;
            line-height: 1.65;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            word-wrap: break-word;
            white-space: pre-wrap;
        }}
        
        .message-bubble.bot {{
            background: {"#1a2632" if theme == "dark" else "#ffffff"};
            border: 1px solid {"#283039" if theme == "dark" else "#e5e7eb"};
            border-top-left-radius: 4px;
            color: {"#ffffff" if theme == "dark" else "#111418"};
        }}
        
        .message-bubble.user {{
            background: linear-gradient(135deg, #2b8cee 0%, #1e40af 100%);
            border-top-right-radius: 4px;
            color: white;
            border: none;
        }}
        
        .image-preview {{
            background: rgba(255, 255, 255, 0.2);
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            margin-top: 0.75rem;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.85rem;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}
        
        /* ========== QUICK BUTTONS ========== */
        .quick-actions-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: {"#9dabb9" if theme == "dark" else "#617589"};
            margin-bottom: 0.75rem;
        }}
        
        div[data-testid="column"] button {{
            background: {"#1a2632" if theme == "dark" else "white"} !important;
            color: {"#ffffff" if theme == "dark" else "#111418"} !important;
            border: 1px solid {"#283039" if theme == "dark" else "#e5e7eb"} !important;
            border-radius: 24px !important;
            font-size: 0.85rem !important;
            font-weight: 500 !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
            width: 100% !important;
        }}
        
        div[data-testid="column"] button:hover {{
            background: linear-gradient(135deg, #2b8cee 0%, #1e40af 100%) !important;
            color: white !important;
            border-color: transparent !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(43, 140, 238, 0.3) !important;
        }}
        
        /* ========== IMAGE BADGE ========== */
        .image-badge {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 0.6rem 1.2rem;
            border-radius: 24px;
            font-size: 0.9rem;
            font-weight: 500;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
        }}
        
        /* ========== INPUT & SEND BUTTON ========== */
        .stTextArea textarea {{
            background: {"#1a2632" if theme == "dark" else "white"} !important;
            border: 2px solid {"#283039" if theme == "dark" else "#e5e7eb"} !important;
            border-radius: 14px !important;
            color: {"#ffffff" if theme == "dark" else "#111418"} !important;
            font-size: 0.95rem !important;
            transition: all 0.2s !important;
            padding: 0.75rem !important;
        }}
        
        .stTextArea textarea:focus {{
            border-color: #2b8cee !important;
            box-shadow: 0 0 0 3px rgba(43, 140, 238, 0.1) !important;
        }}
        
        /* Bouton Envoyer principal */
        button[kind="primary"] {{
            background: linear-gradient(135deg, #2b8cee 0%, #1e40af 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            padding: 0.75rem 2rem !important;
            transition: all 0.2s !important;
            box-shadow: 0 4px 12px rgba(43, 140, 238, 0.3) !important;
        }}
        
        button[kind="primary"]:hover {{
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(43, 140, 238, 0.4) !important;
        }}
        
        /* Bouton Retirer */
        button[key="remove_img"] {{
            background: #ef4444 !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-size: 0.85rem !important;
            padding: 0.5rem 1rem !important;
        }}
        
        button[key="remove_img"]:hover {{
            background: #dc2626 !important;
        }}
        
        /* ========== SIDEBAR ========== */
        section[data-testid="stSidebar"] {{
            background: {"#111418" if theme == "dark" else "#ffffff"} !important;
            border-right: 1px solid {"#283039" if theme == "dark" else "#e5e7eb"} !important;
        }}
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {{
            color: {"#ffffff" if theme == "dark" else "#111418"};
        }}
        
        /* Toggle theme button */
        .theme-toggle-btn {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.5rem 0.75rem !important;
            font-size: 1.2rem !important;
            transition: transform 0.2s !important;
        }}
        
        .theme-toggle-btn:hover {{
            transform: scale(1.05) !important;
        }}
        
        /* ========== EXPANDER ========== */
        .streamlit-expanderHeader {{
            background: {"#1a2632" if theme == "dark" else "#f9fafb"} !important;
            border: 1px solid {"#283039" if theme == "dark" else "#e5e7eb"} !important;
            border-radius: 10px !important;
            font-weight: 500 !important;
            color: {"#ffffff" if theme == "dark" else "inherit"} !important;
        }}
        
        /* ========== RESPONSIVE ========== */
        @media (max-width: 768px) {{
            .message-content {{
                max-width: 85%;
            }}
            .header-title {{
                font-size: 1.5rem;
            }}
        }}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
        st.session_state.theme_initialized = True

    def _nettoyer_reponse(self, texte: str) -> str:
        """Nettoie la réponse de l'IA en supprimant les avertissements dupliqués et le HTML"""
        # Supprimer les balises HTML
        texte = re.sub(r'<[^>]+>', '', texte)
        
        # Supprimer les avertissements en double (garder seulement le premier)
        parties = texte.split('---')
        if len(parties) > 1:
            # Garder seulement la partie principale (avant le premier ---)
            texte = parties[0].strip()
        
        # Supprimer les avertissements intégrés
        patterns = [
            r'⚠️.*?AVERTISSEMENT.*?\n.*?\n.*?\n',
            r'---\s*⚠️.*?SAMU\)\s*',
            r'\*\*AVERTISSEMENT.*?\*\*.*?SAMU\)\.?'
        ]
        
        for pattern in patterns:
            texte = re.sub(pattern, '', texte, flags=re.DOTALL | re.IGNORECASE)
        
        return texte.strip()

    def afficher_entete(self):
        """Affiche l'en-tête de l'application"""
        theme = "🌙 Mode sombre" if st.session_state.dark_mode else "☀️ Mode clair"
        
        st.markdown(f"""
        <div class="modern-header">
            <div class="header-title">
                🫁 PneumoScan AI
            </div>
            <div class="header-subtitle">
                <span class="status-dot"></span>
                Assistant Médical Intelligent · Analyse de Pneumonie
                <span style="margin-left: auto; font-size: 0.8rem; opacity: 0.8;">{theme}</span>
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
                Vérifiez toujours avec un professionnel de santé. 
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
                # Utiliser un bouton custom avec CSS
                theme_label = "🌙" if not st.session_state.dark_mode else "☀️"
                theme_help = "Passer en mode clair" if st.session_state.dark_mode else "Passer en mode sombre"
                
                if st.button(theme_label, key="theme_toggle", help=theme_help):
                    st.session_state.dark_mode = not st.session_state.dark_mode
                    st.rerun()
            
            st.markdown("---")
            st.markdown("### 📊 État du Système")
            
            # Afficher le thème actuel
            theme_status = "🌙 Activé" if st.session_state.dark_mode else "☀️ Activé"
            st.info(f"**Thème:** {theme_status}")
            
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
            # Nettoyer le contenu
            content = self._nettoyer_reponse(message["content"])
            
            if message["role"] == "user":
                image_html = ""
                if message.get("has_image"):
                    image_html = f'<div class="image-preview">📸 {message.get("image_name", "image.jpg")}</div>'
                
                st.markdown(f"""
                <div class="message-wrapper user">
                    <div class="avatar user">👤</div>
                    <div class="message-content">
                        <div class="message-header">
                            <span class="message-author">Vous</span>
                            <span class="message-time">maintenant</span>
                        </div>
                        <div class="message-bubble user">{content}{image_html}</div>
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
                        <div class="message-bubble bot">{content}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Zone de saisie
        st.markdown("---")
        
        # Questions rapides
        st.markdown('<p class="quick-actions-title">💡 Questions rapides:</p>', unsafe_allow_html=True)
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
        
        st.markdown("<br>", unsafe_allow_html=True)
        
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
            placeholder="Posez votre question sur la pneumonie...",
            height=100,
            key="user_input",
            label_visibility="collapsed"
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
        
        with st.spinner("🤖 Analyse en cours..."):
            try:
                response = st.session_state.assistant.chat(
                    message_utilisateur=user_input,
                    image_bytes=st.session_state.current_image,
                    conversation_history=st.session_state.conversation_history[:-1]
                )
                
                # Nettoyer la réponse
                response_clean = self._nettoyer_reponse(response)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_clean
                })
                
                st.session_state.conversation_history.append({
                    "role": "assistant",
                    "content": response_clean
                })
                
                if st.session_state.current_image:
                    st.session_state.current_image = None
                    st.session_state.image_name = None
                
                st.rerun()
                
            except Exception as e:
                # Gestion des erreurs
                error_message = f"""
⚠️ **Erreur lors du traitement**
Une erreur est survenue lors de l'analyse. Veuillez réessayer.

Détails techniques : {str(e)[:100]}
"""
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
                
                st.session_state.conversation_history.append({
                    "role": "assistant", 
                    "content": error_message
                })
            
            # Réinitialiser l'input utilisateur
            st.session_state.user_input = ""
            
            # Rafraîchir l'affichage
            st.rerun()

    def _exporter_conversation(self):
        """Exporte la conversation au format JSON"""
        try:
            import json
            from datetime import datetime
            
            # Préparer les données d'export
            export_data = {
                "export_date": datetime.now().isoformat(),
                "application": "PneumoScan AI",
                "version": "1.0",
                "messages": st.session_state.messages,
                "metadata": {
                    "total_messages": len(st.session_state.messages),
                    "has_image": st.session_state.current_image is not None,
                    "image_name": st.session_state.image_name
                }
            }
            
            # Convertir en JSON formaté
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            # Créer le bouton de téléchargement
            filename = f"conversation_pneumoscan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.download_button(
                    label="📥 Télécharger au format JSON",
                    data=json_str,
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True
                )
            with col2:
                if st.button("📋 Copier", use_container_width=True):
                    st.code(json_str[:500] + "..." if len(json_str) > 500 else json_str)
            
        except Exception as e:
            st.error(f"❌ Erreur d'exportation : {str(e)}")

    def afficher_statistiques(self):
        """Affiche les statistiques et informations système"""
        with st.expander("📊 Statistiques système", expanded=False):
            # Informations de base
            st.markdown("### 📈 Métriques")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Messages", len(st.session_state.messages))
            with col2:
                user_messages = sum(1 for m in st.session_state.messages if m["role"] == "user")
                st.metric("Vos messages", user_messages)
            with col3:
                assistant_messages = sum(1 for m in st.session_state.messages if m["role"] == "assistant")
                st.metric("Réponses IA", assistant_messages)
            
            st.markdown("---")
            st.markdown("### 🖼️ État des images")
            
            if st.session_state.current_image:
                st.success("✅ Image prête pour analyse")
                st.info(f"Nom : {st.session_state.image_name}")
            else:
                st.info("📭 Aucune image attachée")
            
            st.markdown("---")
            st.markdown("### 🤖 État de l'IA")
            
            if st.session_state.assistant.use_gpt4:
                st.success("✅ GPT-4 actif")
            else:
                st.warning("⚠️ Mode local (réponses basiques)")
                
            # Tester la connexion au serveur
            try:
                with st.spinner("🔍 Test de connexion..."):
                    response = requests.get("http://localhost:8000/health", timeout=3)
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"✅ Serveur connecté ({response.status_code})")
                        
                        if data.get("model_loaded"):
                            st.success("✅ Modèle chargé")
                        else:
                            st.error("❌ Modèle non chargé")
                            
                    else:
                        st.error(f"❌ Serveur erreur ({response.status_code})")
            except Exception as e:
                st.error(f"❌ Serveur inaccessible : {str(e)[:50]}")

    def afficher_guide(self):
        """Affiche le guide d'utilisation"""
        with st.expander("🎓 Guide d'utilisation", expanded=False):
            st.markdown("""
            ### **Comment utiliser PneumoScan AI**
            
            #### **1. 📤 Télécharger une radiographie**
            - Utilisez le bouton dans la barre latérale
            - Sélectionnez une image (JPG, PNG, JPEG)
            - L'image sera automatiquement attachée à votre prochain message
            
            #### **2. 💬 Poser des questions**
            - **Symptômes** : "Quels sont les symptômes de la pneumonie ?"
            - **Causes** : "Quelles sont les causes de la pneumonie ?"
            - **Traitements** : "Comment traiter la pneumonie ?"
            - **Prévention** : "Comment prévenir la pneumonie ?"
            - **Analyse d'image** : "Peux-tu analyser cette radiographie ?"
            
            #### **3. 🩺 Obtenir des réponses détaillées**
            - **Avec GPT-4** : Réponses complètes avec explications
            - **Avec modèle local** : Réponses basiques sans connexion internet
            - **Avec image** : Analyse automatique de la radiographie
            
            #### **4. 🔧 Fonctionnalités avancées**
            - **Thème sombre/clair** : Bouton 🌙/☀️ dans la barre latérale
            - **Nouvelle conversation** : Réinitialise tout
            - **Export** : Téléchargez la conversation en JSON
            - **Statistiques** : Suivez l'utilisation
            """)
            
            st.markdown("---")
            st.markdown("### **⚠️ Notes importantes**")
            st.markdown("""
            - **Ce n'est pas un outil de diagnostic** : Consultez toujours un médecin
            - **Les urgences** : Appelez le 15 (SAMU) immédiatement
            - **Confidentialité** : Les conversations ne sont pas stockées sur nos serveurs
            - **Précision** : Les résultats dépendent de la qualité des images
            """)

    def afficher_actions_rapides(self):
        """Affiche des actions rapides en bas de l'interface"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Rafraîchir", help="Rafraîchir l'interface", use_container_width=True):
                st.rerun()
        
        with col2:
            if st.button("📋 Exporter", help="Exporter la conversation", use_container_width=True):
                self._exporter_conversation()
        
        with col3:
            if st.button("🗑️ Effacer tout", 
                        help="Effacer toute la conversation", 
                        use_container_width=True,
                        type="secondary"):
                st.session_state.messages = []
                st.session_state.conversation_history = []
                st.session_state.current_image = None
                st.session_state.image_name = None
                if hasattr(st.session_state.assistant, 'reset_conversation'):
                    st.session_state.assistant.reset_conversation()
                st.rerun()

    def lancer_interface(self):
        """Lance l'interface principale"""
        # Appliquer le CSS selon le thème
        self._appliquer_css()
        
        # Afficher l'en-tête
        self.afficher_entete()
        
        # Afficher l'avertissement médical
        self.afficher_avertissement()
        
        # Layout principal en deux colonnes
        col_chat, col_sidebar = st.columns([3, 1])
        
        with col_chat:
            # Interface de chat
            self.afficher_chat()
            
            # Actions rapides
            self.afficher_actions_rapides()
        
        with col_sidebar:
            # Guide d'utilisation
            self.afficher_guide()
            
            # Statistiques système
            self.afficher_statistiques()
            
            # Zone d'attachement d'image
            self.afficher_attacher_image()
        
        # Barre latérale (doit être à la fin pour Streamlit)
        self.afficher_sidebar()

def main():
    """Fonction principale"""
    # Vérification des dépendances et structure
    try:
        # Vérifier que l'assistant peut être importé
        import os
        
        # Afficher un message de démarrage
        st.info("""
        🚀 **PneumoScan AI** - Démarrage...
        Vérification de la configuration système.
        """)
        
        # Vérifier si le serveur est accessible
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code != 200:
                st.warning("⚠️ Le serveur de classification n'est pas accessible. L'analyse d'images ne fonctionnera pas.")
        except:
            st.warning("⚠️ Le serveur de classification n'est pas démarré. Lancez-le avec `python serveur_medical.py`")
        
        # Créer et lancer l'interface
        interface = InterfaceMediBot()
        interface.lancer_interface()
        
    except ImportError as e:
        st.error(f"❌ Erreur d'importation : {str(e)}")
        st.markdown("""
        **Vérifiez les points suivants :**
        1. Le fichier `assistant_medical.py` existe dans `src/chatbot/`
        2. Tous les modules requis sont installés
        3. La structure des dossiers est correcte
        """)
        
    except Exception as e:
        st.error(f"❌ Erreur critique : {str(e)}")
        st.markdown("""
        **Dépannage :**
        1. Vérifiez que tous les services sont lancés
        2. Consultez les logs pour plus d'informations
        3. Redémarrez l'application
        """)

# Point d'entrée principal
if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Lancer l'application
    main()