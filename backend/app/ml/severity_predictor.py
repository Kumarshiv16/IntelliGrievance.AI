"""
IntelliGrievance AI - Severity & Priority Prediction Engine
Independent supervised severity classifier + Institutional Safety Safeguard Override.
Distinguishes urgency within categories and enforces human-in-the-loop safeguards
for safety, ragging, assault, suicide, fire, food poisoning, or extreme electrical hazards.
"""

import os
import re
import joblib
import numpy as np
from ml.preprocessing.text_cleaner import clean_text

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models", "severity_pipeline.joblib")

# SLA Response times in hours based on institutional policy
SLA_HOURS = {
    "Critical": 4,      # Immediate intervention within 4 hours
    "High": 24,         # 24-hour turnaround
    "Medium": 72,       # 3 business days
    "Low": 168          # 7 calendar days
}

# Severity numerical score weights (0 - 100)
SEVERITY_WEIGHTS = {
    "Low": 20.0,
    "Medium": 45.0,
    "High": 75.0,
    "Critical": 98.0
}

# Regex safeguard: guarantees high-risk complaints cannot be downgraded without human clearance
SAFEGUARD_CRITICAL_PATTERN = re.compile(
    r"\b(rag(ging|ged)?|harass(ment)?|assault(ed)?|threat(ened|ening)?|extort(ion)?|"
    r"fire|flames|smoke|burning|short circuit|electrocution|electric shock|"
    r"suicide|depression|self-harm|ambulance|hospital(ized)?|food poisoning|"
    r"weapon|iron rod|knife|molest(ation|ed)?|stalk(ing|ed)?|bleeding|collapse(d)?)\b",
    re.IGNORECASE
)

class SeverityPredictorEngine:
    def __init__(self):
        self.model = None
        self._load_model()
        
    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"Warning: Could not load severity model: {e}")
                
    def predict(self, text: str, predicted_category: str = None) -> dict:
        if not self.model:
            self._load_model()
        if not self.model:
            raise RuntimeError("Severity model pipeline is not trained or found.")
            
        cleaned = clean_text(text)
        probs = self.model.predict_proba([cleaned])[0]
        classes = self.model.classes_
        prob_dict = {str(c): float(p) for c, p in zip(classes, probs)}
        
        raw_pri = classes[np.argmax(probs)]
        
        # Calculate continuous severity score (0 to 100)
        continuous_score = sum(prob_dict.get(k, 0.0) * SEVERITY_WEIGHTS[k] for k in SEVERITY_WEIGHTS)
        
        # Check Safety Safeguard Rules
        safeguard_triggered = False
        safeguard_reason = None
        
        match = SAFEGUARD_CRITICAL_PATTERN.search(text)
        if match:
            safeguard_triggered = True
            safeguard_reason = f"Safety risk token detected: '{match.group(0)}'"
        elif predicted_category == "Safety and Harassment" and raw_pri in ("Low", "Medium"):
            safeguard_triggered = True
            safeguard_reason = "Safety and Harassment category default policy: Minimum priority escalated to High"
            
        final_pri = raw_pri
        if safeguard_triggered:
            if match:
                final_pri = "Critical"
                continuous_score = max(continuous_score, 94.0)
            elif predicted_category == "Safety and Harassment":
                final_pri = "High" if raw_pri in ("Low", "Medium") else raw_pri
                continuous_score = max(continuous_score, 78.0)
                
        return {
            "priority": str(final_pri),
            "raw_model_priority": str(raw_pri),
            "severity_score": round(float(continuous_score), 1),
            "sla_hours": SLA_HOURS[str(final_pri)],
            "safeguard_override": safeguard_triggered,
            "safeguard_reason": safeguard_reason,
            "priority_probabilities": {k: round(float(v), 4) for k, v in prob_dict.items()}
        }

severity_engine = SeverityPredictorEngine()
