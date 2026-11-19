"""
IntelliGrievance AI - AI Services Endpoints
Endpoints for:
- Live classification and severity preview with full explainability.
- Semantic similarity computation and duplicate detection.
- Department routing suggestions.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.schemas import AIPreviewRequest, AIPreviewResponse
from backend.app.ml.category_classifier import category_engine
from backend.app.ml.severity_predictor import severity_engine
from backend.app.ml.explainability import explainability_engine
from backend.app.ml.routing_engine import routing_engine
from backend.app.ml.semantic_similarity import similarity_engine
from backend.app.models.entities import Grievance

router = APIRouter(prefix="/ai", tags=["AI & NLP Engine"])

@router.post("/preview", response_model=AIPreviewResponse)
def preview_ai_analysis(req: AIPreviewRequest, db: Session = Depends(get_db)):
    text = req.text.strip()
    
    # 1. Category Classification
    cat_res = category_engine.predict(text)
    category = cat_res["category"]
    confidence = cat_res["confidence"]
    top_categories = cat_res["top_categories"]
    
    # 2. Severity & Urgency Prediction + Safeguards
    sev_res = severity_engine.predict(text, predicted_category=category)
    priority = sev_res["priority"]
    
    # 3. Department Routing
    route_res = routing_engine.route_grievance(category, priority)
    
    # 4. Explainable AI Feature Attribution
    xai_res = explainability_engine.explain_prediction(text)
    
    # 5. Semantic Similarity / Duplicate Detection against open grievances
    open_cases = db.query(Grievance).filter(Grievance.status.in_(["Submitted", "Under Review", "Assigned", "In Progress"])).limit(40).all()
    candidates = [{"id": g.ticket_id, "text": g.description, "category": g.category, "status": g.status} for g in open_cases]
    duplicates = similarity_engine.find_duplicates(text, candidates)
    
    return {
        "category": category,
        "confidence": confidence,
        "top_categories": top_categories,
        "priority": priority,
        "raw_model_priority": sev_res["raw_model_priority"],
        "severity_score": sev_res["severity_score"],
        "sla_hours": sev_res["sla_hours"],
        "safeguard_override": sev_res["safeguard_override"],
        "safeguard_reason": sev_res["safeguard_reason"],
        "priority_probabilities": sev_res["priority_probabilities"],
        "recommended_department": route_res["recommended_department"],
        "department_code": route_res["department_code"],
        "escalation_hierarchy": route_res["escalation_hierarchy"],
        "explainability": xai_res,
        "potential_duplicates": duplicates[:3]
    }
