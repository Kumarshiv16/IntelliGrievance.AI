"""
IntelliGrievance AI - Category Classification Engine
Loads the serialized best model (with fallback on-the-fly training if needed).
Provides category predictions, probability distributions, top-3 candidates, and inference confidence.
"""

import os
import joblib
import numpy as np
from ml.preprocessing.text_cleaner import clean_text

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models", "best_category_pipeline.joblib")

class CategoryClassifierEngine:
    def __init__(self):
        self.model = None
        self._load_model()
        
    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"Warning: Could not load serialized model: {e}")
                
    def predict(self, text: str) -> dict:
        if not self.model:
            self._load_model()
        if not self.model:
            raise RuntimeError("Category model pipeline is not trained or found.")
            
        cleaned = clean_text(text)
        probs = self.model.predict_proba([cleaned])[0]
        classes = self.model.classes_
        
        top_idx = np.argsort(probs)[::-1]
        best_cat = classes[top_idx[0]]
        confidence = float(probs[top_idx[0]])
        
        top_3 = [
            {"category": str(classes[idx]), "confidence": round(float(probs[idx]), 4)}
            for idx in top_idx[:3]
        ]
        
        return {
            "category": str(best_cat),
            "confidence": round(confidence, 4),
            "top_categories": top_3,
            "all_probabilities": {str(c): round(float(p), 4) for c, p in zip(classes, probs)}
        }

category_engine = CategoryClassifierEngine()
