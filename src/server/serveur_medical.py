from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import torch
from torchvision import transforms, models
import torch.nn as nn
import io
import uvicorn
import os
import sys
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ajouter le chemin source pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

app = FastAPI(
    title="MediBot MCP Server",
    description="Model Context Protocol Server for Pneumonia Classification",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PneumoniaClassifier:
    def __init__(self, model_path: str):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.model = self._load_model()
        self.transform = self._get_transforms()
        self.class_names = ['NORMAL', 'PNEUMONIA']
        logger.info("Classificateur de pneumonie initialisé")

    def _create_model_architecture(self):
        """Crée l'architecture du modèle identique à l'entraînement"""
        model = models.resnet50(pretrained=False)
        num_ftrs = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(num_ftrs, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.1),
            nn.Linear(256, 2)
        )
        return model

    def _load_model(self):
        """Charge le modèle entraîné"""
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Fichier modèle non trouvé: {self.model_path}")
                return None
            
            logger.info(f"Chargement du modèle depuis: {self.model_path}")
            model = self._create_model_architecture()
            
            # Charger les poids
            if self.model_path.endswith('_inference.pth'):
                state_dict = torch.load(self.model_path, map_location=self.device)
                model.load_state_dict(state_dict)
            else:
                checkpoint = torch.load(self.model_path, map_location=self.device)
                if 'model_state_dict' in checkpoint:
                    model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    model.load_state_dict(checkpoint)
            
            model.eval()
            model.to(self.device)
            logger.info("Modèle chargé avec succès")
            return model
            
        except Exception as e:
            logger.error(f"Erreur chargement modèle: {e}")
            return None

    def _get_transforms(self):
        """Transformations identiques à l'entraînement"""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, image_bytes: bytes) -> dict:
        """Prédit sur une image"""
        try:
            if self.model is None:
                return {"error": "Modèle non chargé", "status": "error"}

            # Conversion bytes → image
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Transformation
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Prédiction
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, prediction = torch.max(probabilities, 1)
            
            return {
                'prediction': self.class_names[prediction.item()],
                'confidence': confidence.item(),
                'probabilities': {
                    'NORMAL': probabilities[0][0].item(),
                    'PNEUMONIA': probabilities[0][1].item()
                },
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Erreur prédiction: {e}")
            return {'error': str(e), 'status': 'error'}

# Initialisation du classifieur
model_path = os.getenv('MODEL_PATH', 'models/pneumonia_classifier_inference_20251115_163236.pth')
classifier = PneumoniaClassifier(model_path)

@app.get("/")
async def root():
    return {
        "message": "MediBot MCP Server - Classification Pneumonie",
        "status": "running",
        "model_loaded": classifier.model is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "model_loaded": classifier.model is not None,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict")
async def predict_pneumonia(file: UploadFile = File(...)):
    """
    Endpoint pour la classification de pneumonie
    """
    try:
        # Vérification du type de fichier
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Le fichier doit être une image")
        
        # Vérification de la taille (max 10MB)
        file.file.seek(0, 2)  # aller à la fin
        file_size = file.file.tell()
        file.file.seek(0)  # revenir au début
        
        max_size = int(os.getenv('MAX_FILE_SIZE_MB', 10)) * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(status_code=400, detail=f"Fichier trop volumineux. Maximum: {max_size//(1024*1024)}MB")
        
        # Lecture de l'image
        image_bytes = await file.read()
        
        # Prédiction
        result = classifier.predict(image_bytes)
        
        if result['status'] == 'error':
            raise HTTPException(status_code=500, detail=result['error'])
        
        logger.info(f"Prédiction effectuée: {result['prediction']} (confiance: {result['confidence']:.2f})")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur traitement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")

@app.get("/model/info")
async def model_info():
    """Retourne les informations du modèle"""
    return {
        "model_name": "ResNet50 Pneumonia Classifier",
        "input_size": "224x224",
        "classes": classifier.class_names,
        "description": "Modèle de classification de pneumonie basé sur ResNet50",
        "model_loaded": classifier.model is not None,
        "device": str(classifier.device)
    }

if __name__ == "__main__":
    port = int(os.getenv("MCP_SERVER_PORT", 8000))
    logger.info(f"🚀 Démarrage du serveur MCP sur le port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)