"""
IntelliGrievance AI - Pydantic Request & Response Schemas
Provides comprehensive typing and validation for:
- Authentication (Register, Login, Token, UserProfile)
- Grievance Filing, Classification, Prediction Preview
- Status & Department Updates
- Comments & Status History
- Explainable AI output & Similarity Search
- Administrative Analytics & KPI summaries
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# ── Auth Schemas ─────────────────────────────────────────────────────────────
class UserRegisterRequest(BaseModel):
    email: str = Field(..., description="User university email address")
    password: str = Field(..., min_length=6)
    full_name: str
    role: str = "student" # student, admin, department_head
    department_code: Optional[str] = None
    roll_number: Optional[str] = None
    academic_department: Optional[str] = "Computer Science and Engineering"
    academic_year: Optional[str] = "3rd Year"
    hostel_block: Optional[str] = None
    phone_number: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# ── Grievance & AI Schemas ────────────────────────────────────────────────────
class AIPreviewRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Student grievance natural language text")
    location: Optional[str] = None

class AIPreviewResponse(BaseModel):
    category: str
    confidence: float
    top_categories: List[Dict[str, Any]]
    priority: str
    raw_model_priority: str
    severity_score: float
    sla_hours: int
    safeguard_override: bool
    safeguard_reason: Optional[str]
    priority_probabilities: Dict[str, float]
    recommended_department: str
    department_code: str
    escalation_hierarchy: List[Dict[str, Any]]
    explainability: Dict[str, Any]
    potential_duplicates: List[Dict[str, Any]] = []

class GrievanceCreateRequest(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=15)
    location: Optional[str] = "General Campus"

class GrievanceStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="Submitted, Under Review, Assigned, In Progress, Escalated, Resolved, Rejected")
    remarks: Optional[str] = None
    resolution_notes: Optional[str] = None

class GrievanceReassignRequest(BaseModel):
    department_code: str
    remarks: Optional[str] = None

class GrievanceCommentCreateRequest(BaseModel):
    comment_text: str = Field(..., min_length=2)
    is_internal_note: bool = False

# ── Department Schemas ───────────────────────────────────────────────────────
class DepartmentResponse(BaseModel):
    id: int
    code: str
    name: str
    head_name: Optional[str]
    contact_email: str
    default_sla_hours: int
    is_active: bool

# ── Analytics Schemas ────────────────────────────────────────────────────────
class AdminAnalyticsResponse(BaseModel):
    kpis: Dict[str, Any]
    by_category: Dict[str, int]
    by_priority: Dict[str, int]
    by_status: Dict[str, int]
    trend_14_days: List[Dict[str, Any]]
    unresolved_hotspots: List[Dict[str, Any]]
    frequent_issue_terms: List[Dict[str, Any]]
    department_workload: List[Dict[str, Any]]
    model_performance: Dict[str, Any]
