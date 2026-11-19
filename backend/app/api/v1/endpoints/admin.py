"""
IntelliGrievance AI - Administration Analytics & Management Endpoints
Provides high-level KPIs, SLA compliance rates, 14-day trends,
geographic hotspot detection, recurrent bigram discovery, and model benchmark cards.
"""

import os
import json
import datetime
from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import CountVectorizer
from backend.app.core.database import get_db
from backend.app.models.entities import Grievance, User, Department, AuditLog
from backend.app.api.deps import require_roles
from backend.app.schemas.schemas import AdminAnalyticsResponse
from backend.app.ml.routing_engine import DEPARTMENT_ROUTING_MAP

router = APIRouter(prefix="/admin", tags=["Administration & Analytics"])

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "ml", "reports")

@router.get("/analytics")
def get_analytics(
    current_user: User = Depends(require_roles("admin")),
    db: Session = Depends(get_db)
):
    grievances = db.query(Grievance).all()
    total = len(grievances)
    
    active_cases = [g for g in grievances if g.status not in ("Resolved", "Rejected")]
    resolved_cases = [g for g in grievances if g.status == "Resolved"]
    open_critical = [g for g in active_cases if g.priority == "Critical"]
    
    avg_score = round(sum(g.severity_score for g in grievances) / total, 1) if total > 0 else 0.0
    resolved_pct = round((len(resolved_cases) / total) * 100, 1) if total > 0 else 0.0
    
    # 1. Distributions
    by_category = dict(Counter(g.category for g in grievances))
    by_priority = dict(Counter(g.priority for g in grievances))
    by_status = dict(Counter(g.status for g in grievances))
    
    # 2. 14-Day Timeline Trend
    today = datetime.date.today()
    days_map = Counter(g.created_at.date().isoformat() for g in grievances if g.created_at)
    trend = [
        {
            "date": (today - datetime.timedelta(days=i)).strftime("%d %b"),
            "count": days_map.get((today - datetime.timedelta(days=i)).isoformat(), 0)
        }
        for i in range(13, -1, -1)
    ]
    
    # 3. Recurring Geographic Hotspots (Location + Category)
    active_locs = [(g.category, g.location) for g in active_cases if g.location and g.location != "General Campus"]
    loc_counts = Counter(active_locs)
    hotspots = [
        {
            "category": cat,
            "location": loc,
            "count": count,
            "avg_severity": round(sum(g.severity_score for g in active_cases if g.category == cat and g.location == loc) / count, 1)
        }
        for (cat, loc), count in loc_counts.most_common(6) if count >= 2
    ]
    
    # 4. Frequent N-gram terms per category
    frequent_terms = []
    if total >= 10:
        for cat in by_category:
            cat_texts = [g.description for g in grievances if g.category == cat]
            if len(cat_texts) >= 3:
                try:
                    cv = CountVectorizer(ngram_range=(2, 2), stop_words="english", max_features=10)
                    matrix = cv.fit_transform(cat_texts)
                    sums = matrix.sum(axis=0).A1
                    words = cv.get_feature_names_out()
                    top_bigrams = sorted(zip(words, sums), key=lambda x: -x[1])[:2]
                    for term, count in top_bigrams:
                        if count >= 2:
                            frequent_terms.append({"category": cat, "term": term, "count": int(count)})
                except Exception:
                    pass
    frequent_terms = sorted(frequent_terms, key=lambda x: -x["count"])[:8]
    
    # 5. Department Workload
    dept_counts = Counter(g.assigned_department for g in active_cases)
    department_workload = [
        {"department": dept, "active_tickets": count}
        for dept, count in dept_counts.most_common(12)
    ]
    
    # 6. Model Evaluation Benchmark Metrics from disk
    model_metrics = {}
    report_file = os.path.join(REPORTS_DIR, "model_evaluation_report.json")
    if os.path.exists(report_file):
        try:
            with open(report_file, "r", encoding="utf-8") as f:
                model_metrics = json.load(f)
        except Exception:
            pass
            
    return {
        "kpis": {
            "total": total,
            "active": len(active_cases),
            "resolved": len(resolved_cases),
            "open_critical": len(open_critical),
            "resolved_pct": resolved_pct,
            "avg_severity": avg_score
        },
        "by_category": by_category,
        "by_priority": by_priority,
        "by_status": by_status,
        "trend_14_days": trend,
        "unresolved_hotspots": hotspots,
        "frequent_issue_terms": frequent_terms,
        "department_workload": department_workload,
        "model_performance": model_metrics
    }

@router.get("/departments")
def list_departments(db: Session = Depends(get_db)):
    departments = db.query(Department).all()
    if not departments:
        # Return fallback routing map directory
        return [
            {
                "id": i + 1,
                "code": info["code"],
                "name": info["department"],
                "contact_email": info["email"],
                "escalation_target": info["escalation_target"],
                "default_sla_hours": info["resolution_sla_days"] * 24,
                "is_active": True
            }
            for i, (cat, info) in enumerate(DEPARTMENT_ROUTING_MAP.items())
        ]
    return [
        {
            "id": d.id,
            "code": d.code,
            "name": d.name,
            "contact_email": d.contact_email,
            "escalation_target": d.escalation_target,
            "default_sla_hours": d.default_sla_hours,
            "is_active": d.is_active
        }
        for d in departments
    ]
