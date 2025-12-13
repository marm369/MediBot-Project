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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MediBot Classification Server",
    description="Serveur de classification de pneumonie pour MediBot",
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
        
        device_name = "GPU" if torch.cuda.is_available() else "CPU"
        logger.info(f"✅ Classificateur initialisé sur {device_name}")

    def _create_model_architecture(self):
        """Crée l'architecture du modèle (doit correspondre à l'entraînement)"""
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
                logger.error(f"❌ Fichier modèle non trouvé: {self.model_path}")
                logger.info("💡 Vérifiez que le chemin du modèle est correct")
                return None
            
            logger.info(f"📂 Chargement du modèle depuis: {self.model_path}")
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
            logger.info("✅ Modèle chargé avec succès")
            return model
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            return None

    def _get_transforms(self):
        """Transformations d'image (identiques à l'entraînement)"""
        return transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

    def predict(self, image_bytes: bytes) -> dict:
        """Effectue une prédiction sur une image"""
        try:
            if self.model is None:
                return {
                    "error": "Modèle non chargé. Vérifiez le chemin du fichier modèle.",
                    "status": "error"
                }

            # Convertir bytes → image PIL
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
            # Appliquer les transformations
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Prédiction
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, prediction = torch.max(probabilities, 1)
            
            result = {
                'prediction': self.class_names[prediction.item()],
                'confidence': float(confidence.item()),
                'probabilities': {
                    'NORMAL': float(probabilities[0][0].item()),
                    'PNEUMONIA': float(probabilities[0][1].item())
                },
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Prédiction: {result['prediction']} (confiance: {result['confidence']:.2%})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction: {e}")
            return {
                'error': str(e),
                'status': 'error'
            }

# Initialisation du classifieur
model_path = os.getenv('MODEL_PATH', 'models/pneumonia_classifier_inference.pth')
classifier = PneumoniaClassifier(model_path)

@app.get("/")
async def root():
    """Point d'entrée principal"""
    return {
        "service": "MediBot Classification Server",
        "status": "running",
        "model_loaded": classifier.model is not None,
        "model_path": model_path,
        "device": str(classifier.device),
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST)",
            "model_info": "/model/info"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de l'état du serveur"""
    return {
        "status": "healthy" if classifier.model is not None else "degraded",
        "model_loaded": classifier.model is not None,
        "device": str(classifier.device),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict")
async def predict_pneumonia(file: UploadFile = File(...)):
    """
    Endpoint de prédiction
    
    Args:
        file: Image de radiographie (JPEG/PNG)
        
    Returns:
        Résultat de classification avec probabilités
    """
    try:
        logger.info(f"📸 Nouvelle requête de prédiction - Fichier: {file.filename}")
        
        # Vérification du type de fichier
        if not file.content_type.startswith('image/'):
            logger.warning(f"⚠️ Type de fichier invalide: {file.content_type}")
            raise HTTPException(
                status_code=400,
                detail="Le fichier doit être une image (JPEG, PNG)"
            )
        
        # Vérification de la taille (max 10MB par défaut)
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        max_size = int(os.getenv('MAX_FILE_SIZE_MB', 10)) * 1024 * 1024
        if file_size > max_size:
            logger.warning(f"⚠️ Fichier trop volumineux: {file_size} bytes")
            raise HTTPException(
                status_code=400,
                detail=f"Fichier trop volumineux. Maximum: {max_size//(1024*1024)}MB"
            )
        
        # Lecture de l'image
        image_bytes = await file.read()
        logger.info(f"✅ Image lue: {len(image_bytes)} bytes")
        
        # Prédiction
        result = classifier.predict(image_bytes)
        
        if result['status'] == 'error':
            logger.error(f"❌ Erreur classification: {result['error']}")
            raise HTTPException(
                status_code=500,
                detail=result['error']
            )
        
        logger.info(f"✅ Prédiction réussie: {result['prediction']}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement: {str(e)}"
        )

@app.get("/model/info")
async def model_info():
    """Informations sur le modèle"""
    return {
        "model_name": "ResNet50 Pneumonia Classifier",
        "architecture": "ResNet50 avec couche FC personnalisée",
        "input_size": "224x224 RGB",
        "classes": classifier.class_names,
        "num_classes": len(classifier.class_names),
        "model_loaded": classifier.model is not None,
        "device": str(classifier.device),
        "model_path": model_path
    }

@app.on_event("startup")
async def startup_event():
    """Actions au démarrage du serveur"""
    logger.info("=" * 50)
    logger.info("🚀 Démarrage du serveur MediBot")
    logger.info("=" * 50)
    if classifier.model is not None:
        logger.info("✅ Serveur prêt à recevoir des requêtes")
    else:
        logger.warning("⚠️ ATTENTION: Modèle non chargé!")
        logger.info(f"💡 Vérifiez le chemin: {model_path}")

if __name__ == "__main__":
    port = int(os.getenv("MCP_SERVER_PORT", 8000))
    logger.info(f"🌐 Lancement du serveur sur http://localhost:{port}")
    logger.info(f"📖 Documentation disponible sur http://localhost:{port}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )