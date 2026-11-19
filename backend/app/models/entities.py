"""
IntelliGrievance AI - Enterprise Relational Database Models
Implements normalized tables:
- users & student_profiles
- departments
- grievances
- grievance_predictions (ML audit data & XAI tokens)
- grievance_status_history
- grievance_comments (internal & student notes)
- audit_logs
- recurring_issue_clusters
"""

import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="student", nullable=False) # student, admin, department_head, staff
    department_code = Column(String(50), nullable=True) # if department officer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    profile = relationship("StudentProfile", back_populates="user", uselist=False)
    grievances = relationship("Grievance", back_populates="student")

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    roll_number = Column(String(100), unique=True, index=True, nullable=False)
    department = Column(String(100), nullable=False)
    academic_year = Column(String(20), nullable=False)
    hostel_block = Column(String(100), nullable=True)
    phone_number = Column(String(50), nullable=True)
    
    user = relationship("User", back_populates="profile")

class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    head_name = Column(String(255), nullable=True)
    contact_email = Column(String(255), nullable=False)
    escalation_target = Column(String(255), nullable=True)
    default_sla_hours = Column(Integer, default=72)
    is_active = Column(Boolean, default=True)

class Grievance(Base):
    __tablename__ = "grievances"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. TKT-2026-0001
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    
    # AI Classification Results
    category = Column(String(100), index=True, nullable=False)
    confidence = Column(Float, nullable=False)
    priority = Column(String(50), index=True, nullable=False) # Critical, High, Medium, Low
    severity_score = Column(Float, nullable=False) # 0 - 100
    sla_hours = Column(Integer, nullable=False)
    
    # Department Routing
    department_code = Column(String(50), index=True, nullable=False)
    assigned_department = Column(String(255), nullable=False)
    
    # Status Lifecycle
    # Submitted -> AI Analyzed -> Under Review -> Assigned -> In Progress -> Escalated -> Resolved -> Rejected
    status = Column(String(50), default="Submitted", index=True, nullable=False)
    resolution_notes = Column(Text, nullable=True)
    
    # Flags & Timestamps
    is_safeguard_override = Column(Boolean, default=False)
    is_potential_duplicate = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    student = relationship("User", back_populates="grievances")
    prediction_details = relationship("GrievancePrediction", back_populates="grievance", uselist=False)
    history = relationship("GrievanceStatusHistory", back_populates="grievance")
    comments = relationship("GrievanceComment", back_populates="grievance")

class GrievancePrediction(Base):
    __tablename__ = "grievance_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), unique=True, nullable=False)
    model_version = Column(String(50), default="1.0.0")
    top_categories_json = Column(Text, nullable=True) # JSON list
    priority_probs_json = Column(Text, nullable=True) # JSON dict
    xai_features_json = Column(Text, nullable=True)   # JSON list of top words
    severity_drivers_json = Column(Text, nullable=True)
    safeguard_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    grievance = relationship("Grievance", back_populates="prediction_details")

class GrievanceStatusHistory(Base):
    __tablename__ = "grievance_status_history"
    
    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=False)
    from_status = Column(String(50), nullable=True)
    to_status = Column(String(50), nullable=False)
    changed_by_user = Column(String(255), nullable=False)
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    grievance = relationship("Grievance", back_populates="history")

class GrievanceComment(Base):
    __tablename__ = "grievance_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    grievance_id = Column(Integer, ForeignKey("grievances.id"), nullable=False)
    author_name = Column(String(255), nullable=False)
    author_role = Column(String(50), nullable=False)
    is_internal_note = Column(Boolean, default=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    grievance = relationship("Grievance", back_populates="comments")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    actor_id = Column(Integer, nullable=True)
    actor_email = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
