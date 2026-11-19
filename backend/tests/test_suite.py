"""
IntelliGrievance AI - Automated Integration & Unit Test Suite
Covers:
- Machine Learning pipelines (Category, Severity, Safeguard Override)
- Explainable AI feature attribution
- Semantic similarity duplicate detection
- Cryptographic authentication & token decoding
- End-to-end database operations and grievance workflows
"""

import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.app.core.database import Base
from backend.app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from backend.app.ml.category_classifier import category_engine
from backend.app.ml.severity_predictor import severity_engine
from backend.app.ml.explainability import explainability_engine
from backend.app.ml.routing_engine import routing_engine
from backend.app.ml.semantic_similarity import similarity_engine
from backend.app.models.entities import User, Grievance

# ── 1. ML Tests ─────────────────────────────────────────────────────────────
def test_category_classification():
    text = "Professor in Data Structures skips lectures regularly and only 30 percent syllabus completed."
    res = category_engine.predict(text)
    assert res["category"] == "Academic"
    assert res["confidence"] > 0.0
    assert len(res["top_categories"]) == 3

def test_hostel_category_and_safeguard():
    text = "Severe ragging by senior students in Hostel Block A, threat of physical violence."
    cat_res = category_engine.predict(text)
    sev_res = severity_engine.predict(text, predicted_category=cat_res["category"])
    
    assert sev_res["priority"] == "Critical"
    assert sev_res["safeguard_override"] is True
    assert sev_res["sla_hours"] == 4

def test_explainability_engine():
    text = "Admit card hall ticket not generated on student portal and final semester examination begins tomorrow."
    xai = explainability_engine.explain_prediction(text)
    assert "top_contributing_features" in xai
    assert "severity_drivers" in xai
    assert any("tomorrow" in d.lower() for d in xai["severity_drivers"])

def test_department_routing():
    route = routing_engine.route_grievance("Hostel", "High")
    assert "Hostel" in route["recommended_department"] or "Warden" in route["recommended_department"]
    assert route["department_code"] == "HOSTEL"
    assert len(route["escalation_hierarchy"]) == 3

def test_semantic_similarity_duplicates():
    query = "Water supply in hostel block C is completely dry for 3 days."
    candidates = [
        {"id": "TKT-001", "text": "Zero running water in Hostel Block C washrooms since morning", "category": "Hostel", "status": "Submitted"},
        {"id": "TKT-002", "text": "Bus route 7 broke down on bypass road", "category": "Transportation", "status": "Submitted"}
    ]
    dupes = similarity_engine.find_duplicates(query, candidates)
    assert len(dupes) >= 1
    assert dupes[0]["grievance_id"] == "TKT-001"

# ── 2. Security & Token Tests ───────────────────────────────────────────────
def test_password_hashing():
    pw = "SuperSecretPassword123!"
    h = hash_password(pw)
    assert verify_password(pw, h) is True
    assert verify_password("WrongPassword", h) is False

def test_jwt_token_cycle():
    payload = {"sub": "101", "role": "admin", "email": "test@univ.edu"}
    token = create_access_token(payload, expires_delta_minutes=60)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "101"
    assert decoded["role"] == "admin"
    assert decoded["email"] == "test@univ.edu"

# ── 3. Database Model Lifecycle Tests ────────────────────────────────────────
def test_database_grievance_lifecycle():
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create user
    user = User(
        email="student.test@univ.edu",
        hashed_password=hash_password("password"),
        full_name="Test Student",
        role="student"
    )
    db.add(user)
    db.commit()
    
    # Create grievance
    g = Grievance(
        ticket_id="TKT-TEST-0001",
        student_id=user.id,
        title="Elevator stuck in block",
        description="Elevator in Science block plunged and got stuck with students inside",
        category="Infrastructure",
        confidence=0.95,
        priority="Critical",
        severity_score=95.0,
        sla_hours=4,
        department_code="ESTATE",
        assigned_department="Estate Maintenance",
        status="Submitted"
    )
    db.add(g)
    db.commit()
    
    saved_g = db.query(Grievance).filter(Grievance.ticket_id == "TKT-TEST-0001").first()
    assert saved_g is not None
    assert saved_g.priority == "Critical"
    assert saved_g.student.full_name == "Test Student"
    
    db.close()
