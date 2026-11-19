"""
IntelliGrievance AI - Grievance Management Endpoints
Provides endpoints for:
- Student submission with automated AI scoring and audit snapshot.
- List / Filter / Search grievances by status, priority, category, department.
- Detailed view with AI explainability, status audit trail, and comments.
- Status updates (Workflow progression) with remarks.
- Internal notes and student-department remarks.
"""

import json
import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.entities import (
    User, Grievance, GrievancePrediction, GrievanceStatusHistory, GrievanceComment, AuditLog
)
from backend.app.schemas.schemas import (
    GrievanceCreateRequest, GrievanceStatusUpdateRequest, GrievanceCommentCreateRequest, GrievanceReassignRequest
)
from backend.app.api.deps import get_current_user, require_roles
from backend.app.ml.category_classifier import category_engine
from backend.app.ml.severity_predictor import severity_engine
from backend.app.ml.routing_engine import routing_engine
from backend.app.ml.explainability import explainability_engine
from backend.app.ml.semantic_similarity import similarity_engine

router = APIRouter(prefix="/grievances", tags=["Grievances"])

@router.post("", status_code=status.HTTP_201_CREATED)
def file_grievance(
    req: GrievanceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    text = req.description.strip()
    
    # 1. AI Categorization
    cat_res = category_engine.predict(text)
    category = cat_res["category"]
    confidence = cat_res["confidence"]
    
    # 2. Severity Prediction + Safeguard Rules
    sev_res = severity_engine.predict(text, predicted_category=category)
    priority = sev_res["priority"]
    severity_score = sev_res["severity_score"]
    sla_hours = sev_res["sla_hours"]
    
    # 3. Department Routing
    route_res = routing_engine.route_grievance(category, priority)
    
    # 4. Check for duplicates
    recent_cases = db.query(Grievance).order_by(Grievance.id.desc()).limit(50).all()
    candidates = [{"id": g.ticket_id, "text": g.description, "category": g.category, "status": g.status} for g in recent_cases]
    duplicates = similarity_engine.find_duplicates(text, candidates)
    is_duplicate = len(duplicates) > 0
    
    # 5. Generate Reference Ticket ID
    year = datetime.datetime.utcnow().year
    count = db.query(Grievance).count() + 1
    ticket_id = f"TKT-{year}-{count:05d}"
    
    grievance = Grievance(
        ticket_id=ticket_id,
        student_id=current_user.id,
        title=req.title,
        description=text,
        location=req.location or "General Campus",
        category=category,
        confidence=confidence,
        priority=priority,
        severity_score=severity_score,
        sla_hours=sla_hours,
        department_code=route_res["department_code"],
        assigned_department=route_res["recommended_department"],
        status="Submitted",
        is_safeguard_override=sev_res["safeguard_override"],
        is_potential_duplicate=is_duplicate
    )
    db.add(grievance)
    db.commit()
    db.refresh(grievance)
    
    # 6. Save Explainability & Prediction snapshot
    xai_res = explainability_engine.explain_prediction(text)
    pred_detail = GrievancePrediction(
        grievance_id=grievance.id,
        top_categories_json=json.dumps(cat_res["top_categories"]),
        priority_probs_json=json.dumps(sev_res["priority_probabilities"]),
        xai_features_json=json.dumps(xai_res["top_contributing_features"]),
        severity_drivers_json=json.dumps(xai_res["severity_drivers"]),
        safeguard_reason=sev_res.get("safeguard_reason")
    )
    db.add(pred_detail)
    
    # 7. Record initial lifecycle history
    history = GrievanceStatusHistory(
        grievance_id=grievance.id,
        from_status=None,
        to_status="Submitted",
        changed_by_user=current_user.full_name,
        remarks=f"Grievance filed and AI analyzed. Routed to {route_res['recommended_department']}."
    )
    db.add(history)
    db.commit()
    
    return {
        "id": grievance.id,
        "ticket_id": grievance.ticket_id,
        "category": grievance.category,
        "priority": grievance.priority,
        "severity_score": grievance.severity_score,
        "assigned_department": grievance.assigned_department,
        "sla_hours": grievance.sla_hours,
        "status": grievance.status,
        "is_potential_duplicate": is_duplicate,
        "created_at": grievance.created_at.isoformat()
    }

@router.get("")
def list_grievances(
    status: str = Query(None),
    priority: str = Query(None),
    category: str = Query(None),
    department_code: str = Query(None),
    search: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Grievance)
    
    # Role-based restriction: students only view their own complaints
    if current_user.role == "student":
        query = query.filter(Grievance.student_id == current_user.id)
    elif current_user.role == "department_head" and current_user.department_code:
        query = query.filter(Grievance.department_code == current_user.department_code)
        
    if status:
        query = query.filter(Grievance.status == status)
    if priority:
        query = query.filter(Grievance.priority == priority)
    if category:
        query = query.filter(Grievance.category == category)
    if department_code:
        query = query.filter(Grievance.department_code == department_code)
    if search:
        query = query.filter(
            (Grievance.ticket_id.ilike(f"%{search}%")) |
            (Grievance.title.ilike(f"%{search}%")) |
            (Grievance.description.ilike(f"%{search}%")) |
            (Grievance.location.ilike(f"%{search}%"))
        )
        
    # Highest urgency and most recent first
    grievances = query.order_by(Grievance.severity_score.desc(), Grievance.created_at.desc()).limit(200).all()
    
    return [
        {
            "id": g.id,
            "ticket_id": g.ticket_id,
            "student_id": g.student_id,
            "title": g.title,
            "description": g.description,
            "location": g.location,
            "category": g.category,
            "confidence": g.confidence,
            "priority": g.priority,
            "severity_score": g.severity_score,
            "sla_hours": g.sla_hours,
            "department_code": g.department_code,
            "assigned_department": g.assigned_department,
            "status": g.status,
            "is_safeguard_override": g.is_safeguard_override,
            "is_potential_duplicate": g.is_potential_duplicate,
            "created_at": g.created_at.isoformat(),
            "updated_at": g.updated_at.isoformat() if g.updated_at else None
        }
        for g in grievances
    ]

@router.get("/{id}")
def get_grievance_detail(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    g = db.query(Grievance).filter(Grievance.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")
        
    # Students can only view their own
    if current_user.role == "student" and g.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Unauthorized access to this grievance.")
        
    pred = db.query(GrievancePrediction).filter(GrievancePrediction.grievance_id == g.id).first()
    history = db.query(GrievanceStatusHistory).filter(GrievanceStatusHistory.grievance_id == g.id).order_by(GrievanceStatusHistory.created_at.asc()).all()
    
    # Filter internal comments for students
    comments_query = db.query(GrievanceComment).filter(GrievanceComment.grievance_id == g.id)
    if current_user.role == "student":
        comments_query = comments_query.filter(GrievanceComment.is_internal_note == False)
    comments = comments_query.order_by(GrievanceComment.created_at.asc()).all()
    
    return {
        "id": g.id,
        "ticket_id": g.ticket_id,
        "student_id": g.student_id,
        "student_name": g.student.full_name if g.student else "Student",
        "student_email": g.student.email if current_user.role != "student" else None,
        "title": g.title,
        "description": g.description,
        "location": g.location,
        "category": g.category,
        "confidence": g.confidence,
        "priority": g.priority,
        "severity_score": g.severity_score,
        "sla_hours": g.sla_hours,
        "department_code": g.department_code,
        "assigned_department": g.assigned_department,
        "status": g.status,
        "resolution_notes": g.resolution_notes,
        "is_safeguard_override": g.is_safeguard_override,
        "is_potential_duplicate": g.is_potential_duplicate,
        "created_at": g.created_at.isoformat(),
        "resolved_at": g.resolved_at.isoformat() if g.resolved_at else None,
        "prediction_details": {
            "top_categories": json.loads(pred.top_categories_json) if pred and pred.top_categories_json else [],
            "priority_probabilities": json.loads(pred.priority_probs_json) if pred and pred.priority_probs_json else {},
            "xai_features": json.loads(pred.xai_features_json) if pred and pred.xai_features_json else [],
            "severity_drivers": json.loads(pred.severity_drivers_json) if pred and pred.severity_drivers_json else [],
            "safeguard_reason": pred.safeguard_reason if pred else None
        } if pred else None,
        "history": [
            {
                "from_status": h.from_status,
                "to_status": h.to_status,
                "changed_by": h.changed_by_user,
                "remarks": h.remarks,
                "timestamp": h.created_at.isoformat()
            }
            for h in history
        ],
        "comments": [
            {
                "id": c.id,
                "author": c.author_name,
                "role": c.author_role,
                "is_internal": c.is_internal_note,
                "comment": c.comment_text,
                "created_at": c.created_at.isoformat()
            }
            for c in comments
        ]
    }

@router.patch("/{id}/status")
def update_status(
    id: int,
    req: GrievanceStatusUpdateRequest,
    current_user: User = Depends(require_roles("admin", "department_head")),
    db: Session = Depends(get_db)
):
    g = db.query(Grievance).filter(Grievance.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")
        
    old_status = g.status
    g.status = req.status
    if req.status == "Resolved":
        g.resolved_at = datetime.datetime.utcnow()
        if req.resolution_notes:
            g.resolution_notes = req.resolution_notes
            
    history = GrievanceStatusHistory(
        grievance_id=g.id,
        from_status=old_status,
        to_status=req.status,
        changed_by_user=f"{current_user.full_name} ({current_user.role})",
        remarks=req.remarks or f"Status transitioned from {old_status} to {req.status}."
    )
    db.add(history)
    db.commit()
    
    return {"message": "Status updated successfully.", "new_status": g.status}

@router.post("/{id}/comments")
def add_comment(
    id: int,
    req: GrievanceCommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    g = db.query(Grievance).filter(Grievance.id == id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance not found.")
        
    # Students cannot add internal notes
    is_internal = req.is_internal_note if current_user.role != "student" else False
    
    comment = GrievanceComment(
        grievance_id=g.id,
        author_name=current_user.full_name,
        author_role=current_user.role,
        is_internal_note=is_internal,
        comment_text=req.comment_text
    )
    db.add(comment)
    db.commit()
    
    return {"message": "Comment posted successfully."}
