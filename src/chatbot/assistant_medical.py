import openai
import os
import sys
import requests
from PIL import Image
import io
import logging
from dotenv import load_dotenv
import requests

# Ajouter le chemin source pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssistantMedicalGPT:
    def __init__(self):
        # Charger la configuration
        self.mcp_server_url = "http://localhost:8000/predict"

        self._load_config()
        
        # Initialiser le client OpenAI
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        self.mcp_url = self.mcp_server_url
        
        # Prompt système pour le chatbot médical
        self.prompt_system = """Vous êtes Dr. IA, un assistant médical spécialisé en radiologie pulmonaire.

VOTRE RÔLE:
- Assistant médical virtuel pour l'analyse des radiographies pulmonaires
- Expliquer les résultats de façon claire, simple et empathique
- Donner des informations éducatives sur la pneumonie
- Toujours recommander de consulter un médecin pour confirmation

COMPÉTENCES:
1. *Analyse de radiographies*: Interpréter les résultats de classification IA
2. *Explication médicale*: Traduire les termes techniques en langage simple
3. *Conseils pratiques*: Donner des recommandations appropriées
4. *Information éducative*: Expliquer ce qu'est la pneumonie, ses causes, symptômes

INSTRUCTIONS IMPORTANTES:
- Pour les analyses d'image: expliquez le résultat (NORMAL/PNEUMONIA) et le niveau de confiance
- Donnez des informations sur ce que signifie le diagnostic
- Fournissez des conseils appropriés selon le résultat
- Insistez sur l'importance d'un avis médical professionnel
- Soyez rassurant mais honnête
- Utilisez un langage accessible sans être trop technique

TONE:
- Professionnel mais accessible
- Empathique et rassurant
- Pédagogique
- Jamais alarmiste

NE JAMAIS:
- Poser un diagnostic définitif
- Recommander des traitements spécifiques
- Remplacer un avis médical qualifié
- Être trop technique sans explication

EXEMPLE DE RÉPONSE:
"Bonjour! Suite à l'analyse de votre radiographie, le système a détecté [NORMAL/PNEUMONIA] avec un niveau de confiance de [X]%. 
Cela signifie que [explication simple]. Je vous recommande de [conseil approprié]. 
N'oubliez pas que ce résultat doit être confirmé par un radiologue."

CAPACITÉS DU SYSTÈME:
Le modèle peut détecter deux conditions:
- NORMAL: Radiographie sans signe de pneumonie
- PNEUMONIA: Radiographie montrant des signes de pneumonie"""

        logger.info("Assistant médical GPT initialisé")

    def _load_config(self):
        """Charge la configuration depuis les variables d'environnement"""
        # Charger depuis .env ou .env.example
        env_file = '.env' if os.path.exists('.env') else '.env.example'
        load_dotenv(env_file)
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.mcp_server_url = os.getenv('MCP_SERVER_URL', 'http://localhost:8000')
        
        if not self.openai_api_key or self.openai_api_key == 'votre_cle_api_openai_ici':
            logger.warning("⚠ Clé API OpenAI non configurée")
            if env_file == '.env.example':
                logger.warning("ℹ Utilisation de .env.example - Créez un fichier .env avec votre vraie clé API")
        
        logger.info(f"🌐 Serveur MCP: {self.mcp_server_url}")

    # def _check_mcp_server(self):
    #     """Vérifie la connexion au serveur MCP"""
    #     try:
    #         response = requests.get(f"{self.mcp_server_url}/health", timeout=10)
    #         return response.status_code == 200
    #     except:
    #         return False





    def _check_mcp_server(self):
        """Vérifie si le serveur MCP est en ligne."""
        try:
            url = "http://localhost:8000/health"
            response = requests.get(url, timeout=3)

            if response.status_code == 200:
                data = response.json()
                return data.get("status") == "healthy"
            return False

        except Exception:
            return False




    def analyser_image(self, image_bytes: bytes, question_utilisateur: str = "") -> str:
        """
        Analyse une image avec le modèle MCP puis génère une explication avec GPT-4
        
        Args:
            image_bytes: Bytes de l'image à analyser
            question_utilisateur: Question spécifique de l'utilisateur
            
        Returns:
            str: Explication générée par GPT-4
        """
        try:
            # Vérifier la connexion au serveur MCP
            if not self._check_mcp_server():
                return "Serveur médical indisponible. Veuillez démarrer le serveur MCP."

            # 1. Envoyer l'image au serveur MCP pour classification
            logger.info("Analyse de l'image par le modèle médical...")
            files = {"file": ("radiographie.jpg", image_bytes, "image/jpeg")}
            response_mcp = requests.post(f"{self.mcp_server_url}/predict", files=files, timeout=30)
            
            if response_mcp.status_code != 200:
                error_msg = response_mcp.text
                logger.error(f"Erreur serveur MCP: {error_msg}")
                return f"Erreur lors de l'analyse médicale: {error_msg}"
            
            resultat_analyse = response_mcp.json()
            
            if resultat_analyse.get('status') != 'success':
                error_msg = resultat_analyse.get('error', 'Erreur inconnue')
                logger.error(f"Erreur analyse: {error_msg}")
                return f"Erreur lors de l'analyse: {error_msg}"
            
            # 2. Préparer les données pour GPT-4
            prediction = resultat_analyse['prediction']
            confidence = resultat_analyse['confidence']
            probabilities = resultat_analyse['probabilities']
            
            # 3. Construire le prompt pour GPT-4
            prompt_utilisateur = self._construire_prompt(prediction, confidence, probabilities, question_utilisateur)
            
            # 4. Appel à GPT-4
            logger.info("Génération de l'explication par GPT-4...")
            reponse = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.prompt_system},
                    {"role": "user", "content": prompt_utilisateur}
                ],
                max_tokens=1500,
                temperature=0.7,
                timeout=30
            )
            
            explanation = reponse.choices[0].message.content
            logger.info("Explication générée avec succès")
            
            return explanation
            
        except requests.exceptions.Timeout:
            logger.error("⏰ Timeout lors de la communication avec le serveur MCP")
            return "Délai d'attente dépassé. Le serveur médical met trop de temps à répondre."
        except requests.exceptions.ConnectionError:
            logger.error("🔌 Erreur de connexion au serveur MCP")
            return "Impossible de se connecter au serveur médical. Vérifiez qu'il est démarré."
        except openai.APITimeoutError:
            logger.error("⏰ Timeout API OpenAI")
            return "Délai dépassé avec l'API OpenAI. Veuillez réessayer."
        except openai.AuthenticationError:
            logger.error("Erreur d'authentification OpenAI")
            return "Erreur d'authentification avec l'API OpenAI. Vérifiez votre clé API."
        except Exception as e:
            logger.error(f" Erreur inattendue: {str(e)}")
            return f" Une erreur inattendue s'est produite: {str(e)}"

    def _construire_prompt(self, prediction: str, confidence: float, probabilities: dict, question_utilisateur: str) -> str:
        """Construit le prompt pour GPT-4 basé sur les résultats de l'analyse"""
        
        base_prompt = f"""
RÉSULTAT DE L'ANALYSE MÉDICALE AUTOMATISÉE:

*Résultats de la classification:*
- *Diagnostic:* {prediction}
- *Niveau de confiance:* {confidence:.1%}
- *Probabilité NORMAL:* {probabilities['NORMAL']:.1%}
- *Probabilité PNEUMONIA:* {probabilities['PNEUMONIA']:.1%}

"""

        if question_utilisateur:
            base_prompt += f"""
QUESTION SPÉCIFIQUE DE L'UTILISATEUR:
"{question_utilisateur}"

"""
        else:
            base_prompt += """
L'utilisateur souhaite une explication de ces résultats.

"""

        base_prompt += """
Veuillez fournir une analyse complète et empathique de ces résultats en:
1. Expliquant ce que signifie ce diagnostic en termes simples
2. Donnant des informations sur la condition détectée
3. Fournissant des conseils appropriés pour la prochaine étape
4. Rappelant l'importance d'une consultation médicale professionnelle

Merci de faire preuve d'empathie et de professionnalisme dans votre réponse.
"""

        return base_prompt

    def chat_direct(self, message_utilisateur: str) -> str:
        """
        Chat direct avec GPT pour questions générales sur la pneumonie
        
        Args:
            message_utilisateur: Question de l'utilisateur
            
        Returns:
            str: Réponse générée par GPT-4
        """
        try:
            reponse = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.prompt_system},
                    {"role": "user", "content": message_utilisateur}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return reponse.choices[0].message.content
        except Exception as e:
            logger.error(f"Erreur chat direct: {str(e)}")
            return f"Erreur lors de la génération de la réponse: {str(e)}"

# Test de l'assistant
if __name__ == "__main__":
    try:
        assistant = AssistantMedicalGPT()
        print("Assistant médical GPT initialisé avec succès!")
        
        # Test de connexion MCP
        if assistant._check_mcp_server():
            print("Serveur MCP connecté")
        else:
            print("Serveur MCP inaccessible")
            
    except Exception as e:
        print(f"Erreur initialisation: {e}")