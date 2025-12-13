import openai
import os
import sys
import requests
from PIL import Image
import io
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssistantMedicalGPT:
    def __init__(self):
        # Charger la configuration
        self._load_config()
        
        # Initialiser le client OpenAI
        self.use_gpt4 = False
        self.client = None
        
        if self.openai_api_key and self.openai_api_key != 'votre_cle_api_openai_ici':
            try:
                self.client = openai.OpenAI(api_key=self.openai_api_key)
                self.use_gpt4 = True
                logger.info("✅ GPT-4 disponible")
            except Exception as e:
                logger.error(f"❌ Erreur initialisation OpenAI: {e}")
                self.client = None
                self.use_gpt4 = False
        else:
            logger.warning("⚠ GPT-4 non disponible - Configurez votre clé API dans .env")
        
        # Prompt système pour GPT-4
        self.prompt_system = """Vous êtes Dr. IA, un assistant médical intelligent spécialisé en pneumologie.

VOTRE RÔLE:
- Converser naturellement avec les patients sur les maladies pulmonaires
- Expliquer les résultats d'analyses d'images médicales de façon claire et pédagogique
- Répondre aux questions sur la pneumonie, les symptômes, traitements et prévention
- Être empathique, rassurant et éducatif

CONTEXTE D'ANALYSE D'IMAGES:
Quand un résultat de classification de radiographie vous est fourni, vous devez:
1. Reformuler le résultat technique en langage accessible
2. Expliquer ce que signifient les probabilités
3. Donner du contexte médical pertinent
4. Rassurer ou alerter selon le résultat
5. TOUJOURS recommander une consultation médicale professionnelle

RÈGLES IMPORTANTES:
- Utilisez un ton chaleureux et professionnel
- Vulgarisez les termes médicaux complexes
- Ne posez JAMAIS de diagnostic définitif
- Insistez sur l'importance de consulter un médecin
- Répondez de manière conversationnelle, pas en liste à puces
- Adaptez votre réponse au contexte de la conversation

AVERTISSEMENTS:
- Rappelez systématiquement que l'IA ne remplace pas un médecin
- En cas de symptômes graves, recommandez d'appeler le 15 (SAMU)
- Soyez prudent avec les recommandations de traitement"""

        # Historique de conversation
        self.conversation_history = []
        
        logger.info("Assistant médical initialisé")

    def _load_config(self):
        """Charge la configuration depuis les variables d'environnement"""
        env_file = '.env' if os.path.exists('.env') else '.env.example'
        load_dotenv(env_file)
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key or self.openai_api_key == 'votre_cle_api_openai_ici':
            logger.warning("⚠ Clé API OpenAI non configurée")

    def analyser_image_via_serveur(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Analyse une image via le serveur de classification
        Retourne le résultat brut de la classification
        """
        try:
            files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
            response = requests.post("http://localhost:8000/predict", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'success':
                    return {
                        'success': True,
                        'data': result
                    }
                else:
                    return {
                        'success': False,
                        'error': result.get('error', 'Erreur inconnue')
                    }
            else:
                return {
                    'success': False,
                    'error': f"Erreur serveur: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur analyse image: {e}")
            return {
                'success': False,
                'error': f"Erreur de connexion au serveur: {str(e)}"
            }

    def chat(self, message_utilisateur: str, image_bytes: bytes = None, conversation_history: List[Dict] = None) -> str:
        """
        Méthode principale de chat conversationnel avec GPT-4
        
        Args:
            message_utilisateur: Le message de l'utilisateur
            image_bytes: Optionnel - Image à analyser
            conversation_history: Historique de la conversation
            
        Returns:
            Réponse de l'assistant
        """
        
        # Vérifier si GPT-4 est disponible
        if not self.use_gpt4 or not self.client:
            return """
❌ GPT-4 n'est pas configuré.

Pour utiliser le chatbot conversationnel, vous devez:
1. Obtenir une clé API OpenAI sur https://platform.openai.com/
2. Créer un fichier .env à la racine du projet
3. Ajouter: OPENAI_API_KEY=votre_cle_api_ici
4. Redémarrer l'application

En attendant, vous pouvez tester le serveur de classification directement.
"""

        try:
            # Préparer les messages pour GPT-4
            messages = [{"role": "system", "content": self.prompt_system}]
            
            # Ajouter l'historique de conversation si fourni
            if conversation_history:
                messages.extend(conversation_history)
            
            # Si une image est fournie, l'analyser d'abord
            contexte_image = ""
            if image_bytes:
                logger.info("📸 Analyse de l'image en cours...")
                resultat_classification = self.analyser_image_via_serveur(image_bytes)
                
                if resultat_classification['success']:
                    data = resultat_classification['data']
                    contexte_image = f"""

[RÉSULTAT DE CLASSIFICATION - À INTÉGRER NATURELLEMENT DANS VOTRE RÉPONSE]
Diagnostic: {data['prediction']}
Confiance: {data['confidence']:.1%}
Probabilités:
- NORMAL: {data['probabilities']['NORMAL']:.1%}
- PNEUMONIA: {data['probabilities']['PNEUMONIA']:.1%}

Reformulez ce résultat de manière pédagogique et accessible dans votre réponse.
"""
                else:
                    contexte_image = f"\n\n[ERREUR ANALYSE IMAGE: {resultat_classification['error']}]"
            
            # Construire le message utilisateur complet
            message_complet = message_utilisateur + contexte_image
            messages.append({"role": "user", "content": message_complet})
            
            # Appeler GPT-4
            logger.info("🤖 Appel à GPT-4...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=800,
                temperature=0.7
            )
            
            reponse_assistant = response.choices[0].message.content
            
            # Ajouter l'avertissement médical
            reponse_complete = reponse_assistant + """

---
⚠️ **AVERTISSEMENT MÉDICAL IMPORTANT**
Ces informations sont fournies par une IA à titre éducatif et ne remplacent pas une consultation médicale professionnelle. En cas de doute ou de symptômes inquiétants, consultez immédiatement un médecin.
🚨 **Urgence médicale: appelez le 15 (SAMU)**
"""
            
            return reponse_complete
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du chat: {e}")
            return f"❌ Erreur: {str(e)}\n\nVérifiez que votre clé API OpenAI est valide et que vous avez des crédits disponibles."

    def reset_conversation(self):
        """Réinitialise l'historique de conversation"""
        self.conversation_history = []

# Test de l'assistant
if __name__ == "__main__":
    try:
        assistant = AssistantMedicalGPT()
        print("✅ Assistant médical initialisé avec succès!")
        
        if assistant.use_gpt4:
            print("\n🤖 GPT-4 est disponible - Test de conversation:")
            reponse = assistant.chat("Bonjour, pouvez-vous m'expliquer ce qu'est la pneumonie ?")
            print(f"\nRéponse: {reponse}")
        else:
            print("\n⚠️ GPT-4 non configuré - Configurez votre clé API dans .env")
        
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")