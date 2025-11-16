import openai
import os
import sys
import requests
from PIL import Image
import io
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import torch
import torch.nn as nn
from torchvision import models, transforms

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AssistantMedicalGPT:
    def __init__(self):
        # Charger la configuration
        self._load_config()
        
        # Initialiser le client OpenAI si disponible
        self.use_gpt4 = False
        self.client = None
        
        if self.openai_api_key and self.openai_api_key != 'votre_cle_api_openai_ici':
            try:
                self.client = openai.OpenAI(api_key=self.openai_api_key)
                self.use_gpt4 = True
                logger.info("✅ GPT-4 disponible pour informations générales")
            except Exception as e:
                logger.error(f"❌ Erreur initialisation OpenAI: {e}")
                self.client = None
                self.use_gpt4 = False
        else:
            logger.warning("⚠ GPT-4 non disponible - utilisation des réponses prédéfinies")
        
        # Prompt système pour GPT-4
        self.prompt_system = """Vous êtes Dr. IA, un assistant médical intelligent.

VOTRE RÔLE PRINCIPAL:
- Expliquer les résultats médicaux de façon claire et pédagogique
- Répondre aux questions générales sur la santé pulmonaire
- Fournir des informations éducatives sur les maladies respiratoires

INSTRUCTIONS IMPORTANTES:
- Insistez toujours sur l'importance d'un avis médical professionnel
- Soyez empathique et rassurant
- Utilisez un langage accessible
- Ne posez jamais de diagnostic définitif
- Ne remplacez pas un avis médical qualifié

DOMAINES D'EXPERTISE:
- Pneumologie et maladies respiratoires
- Symptômes et traitements
- Prévention et mode de vie sain
- Explications des procédures médicales"""

        logger.info("Assistant médical initialisé")

    def _load_config(self):
        """Charge la configuration depuis les variables d'environnement"""
        env_file = '.env' if os.path.exists('.env') else '.env.example'
        load_dotenv(env_file)
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key or self.openai_api_key == 'votre_cle_api_openai_ici':
            logger.warning("⚠ Clé API OpenAI non configurée - mode local uniquement")

    def analyser_image_via_serveur(self, image_bytes: bytes, question_utilisateur: str = "") -> str:
        """
        Analyse une image via le serveur de classification
        """
        try:
            files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
            response = requests.post("http://localhost:8000/predict", files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result['status'] == 'success':
                    reponse_base = self._construire_reponse_locale(result, question_utilisateur)
                    
                    # Si GPT-4 est disponible et que l'utilisateur demande des explications, enrichir la réponse
                    if self.use_gpt4 and ("explication" in question_utilisateur.lower() or "explique" in question_utilisateur.lower()):
                        try:
                            reponse_enrichie = self.client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {"role": "system", "content": self.prompt_system},
                                    {"role": "user", "content": f"Voici le résultat d'une analyse de radiographie: {result}. L'utilisateur demande: {question_utilisateur}. Fournissez une explication claire et pédagogique."}
                                ],
                                max_tokens=300,
                                temperature=0.7
                            )
                            return reponse_base + "\n\n💡 **Explications détaillées:**\n" + reponse_enrichie.choices[0].message.content
                        except Exception as e:
                            logger.error(f"Erreur GPT-4: {e}")
                            return reponse_base
                    
                    return reponse_base
                else:
                    return f"❌ Erreur lors de l'analyse: {result.get('error', 'Erreur inconnue')}"
            else:
                return f"❌ Erreur serveur: {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ Erreur analyse image: {e}")
            return f"❌ Erreur lors de l'analyse de l'image: {str(e)}"

    def _construire_reponse_locale(self, resultat: Dict[str, Any], question: str) -> str:
        """Construit une réponse basée sur les résultats de classification"""
        prediction = resultat['prediction']
        confidence = resultat['confidence']
        prob_normal = resultat['probabilities']['NORMAL']
        prob_pneumonia = resultat['probabilities']['PNEUMONIA']
        
        # Réponse de base
        if prediction == 'NORMAL':
            base_reponse = f"""
📊 RÉSULTAT DE L'ANALYSE

🎯 Diagnostic: {prediction}
📈 Niveau de confiance: {confidence:.1%}

📋 Détails:
- Probabilité NORMAL: {prob_normal:.1%}
- Probabilité PNEUMONIA: {prob_pneumonia:.1%}

💡 Explication:
L'analyse ne détecte pas de signes évidents de pneumonie sur cette radiographie.
"""
        else:
            base_reponse = f"""
📊 RÉSULTAT DE L'ANALYSE

🎯 Diagnostic: {prediction}
📈 Niveau de confiance: {confidence:.1%}

📋 Détails:
- Probabilité NORMAL: {prob_normal:.1%}
- Probabilité PNEUMONIA: {prob_pneumonia:.1%}

💡 Explication:
L'analyse détecte des signes évocateurs de pneumonie.
"""

        # Avertissement médical
        base_reponse += f"""

⚠ AVERTISSEMENT MÉDICAL IMPORTANT
Ce résultat est fourni par une intelligence artificielle et ne remplace pas un diagnostic médical professionnel. 
Consultez toujours un médecin qualifié pour toute décision médicale.
"""

        return base_reponse

    def repondre_question_generale(self, question: str) -> str:
        """
        Répond aux questions générales en utilisant GPT-4 ou des réponses prédéfinies
        """
        # Si GPT-4 est disponible, l'utiliser pour les questions complexes
        if self.use_gpt4 and self.client:
            try:
                reponse = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.prompt_system},
                        {"role": "user", "content": question}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                return reponse.choices[0].message.content + """

⚠ AVERTISSEMENT MÉDICAL IMPORTANT
Ces informations sont fournies à titre éducatif et ne remplacent pas une consultation médicale. 
Consultez toujours un professionnel de santé pour tout problème médical.
"""
            except Exception as e:
                logger.error(f"Erreur GPT-4: {e}")
                # Fallback sur les réponses prédéfinies

        # Questions/réponses prédéfinies pour le mode local
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

        # Vérifier si c'est une question prédéfinie
        question_lower = question.lower()
        for key, response in faqs.items():
            if key in question_lower:
                return response

        # Réponse par défaut pour le mode local
        return """
Je suis spécialisé dans l'analyse des radiographies pulmonaires. 

Pour des questions médicales spécifiques, je vous recommande de:
• Consulter un médecin généraliste
• Visiter un service d'urgences en cas de symptômes graves
• Contacter un pneumologue pour des problèmes pulmonaires

📞 En cas d'urgence: Appelez le 15 (SAMU)

⚠ AVERTISSEMENT MÉDICAL IMPORTANT
Ces informations ne remplacent pas une consultation médicale professionnelle.
"""

    def chat(self, message_utilisateur: str, image_bytes: bytes = None) -> str:
        """
        Méthode principale de chat qui combine analyse d'images et questions générales
        """
        # Si une image est fournie, priorité à l'analyse d'image
        if image_bytes:
            return self.analyser_image_via_serveur(image_bytes, message_utilisateur)
        
        # Sinon, répondre à la question générale
        return self.repondre_question_generale(message_utilisateur)

# Test de l'assistant
if __name__ == "__main__":
    try:
        assistant = AssistantMedicalGPT()
        print("✅ Assistant médical initialisé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")