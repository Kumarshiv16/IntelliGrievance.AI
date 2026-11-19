"""
IntelliGrievance AI - Automated Department Routing Engine
Maps categorized grievances to responsible university administrative offices.
Includes configurable departmental routing, escalation paths, and automated workload weighting.
"""

# Default Institutional Department Directory
DEPARTMENT_ROUTING_MAP = {
    "Academic": {
        "department": "Dean of Academic Affairs",
        "code": "ACAD",
        "email": "dean.academics@university.edu",
        "escalation_target": "Vice Chancellor Academic Council",
        "resolution_sla_days": 5
    },
    "Examination": {
        "department": "Controller of Examinations Cell",
        "code": "COE",
        "email": "coe@university.edu",
        "escalation_target": "Registrar Examination Board",
        "resolution_sla_days": 3
    },
    "Hostel": {
        "department": "Chief Warden & Hostel Administration",
        "code": "HOSTEL",
        "email": "chief.warden@university.edu",
        "escalation_target": "Dean Student Welfare",
        "resolution_sla_days": 3
    },
    "Transportation": {
        "department": "Transport Management Department",
        "code": "TRANS",
        "email": "transport@university.edu",
        "escalation_target": "Estate Officer & Admin Registrar",
        "resolution_sla_days": 4
    },
    "Financial": {
        "department": "Accounts, Finance & Scholarship Cell",
        "code": "FIN",
        "email": "accounts@university.edu",
        "escalation_target": "Chief Finance Officer (CFO)",
        "resolution_sla_days": 7
    },
    "Administration": {
        "department": "Registrar & General Administration",
        "code": "ADMIN",
        "email": "registrar@university.edu",
        "escalation_target": "Vice Chancellor Office",
        "resolution_sla_days": 5
    },
    "Faculty": {
        "department": "Faculty Grievance & Ethics Committee",
        "code": "FAC_COMM",
        "email": "faculty.ethics@university.edu",
        "escalation_target": "Pro-Vice Chancellor Academic Integrity",
        "resolution_sla_days": 7
    },
    "Infrastructure": {
        "department": "Estate Maintenance & Works Department",
        "code": "ESTATE",
        "email": "estate.works@university.edu",
        "escalation_target": "Campus Superintending Engineer",
        "resolution_sla_days": 3
    },
    "Library": {
        "department": "University Central Library Administration",
        "code": "LIB",
        "email": "chief.librarian@university.edu",
        "escalation_target": "Dean Academic Resources",
        "resolution_sla_days": 4
    },
    "IT Support": {
        "department": "IT Infrastructure & ERP Helpdesk",
        "code": "IT",
        "email": "it.support@university.edu",
        "escalation_target": "Chief Information Officer (CIO)",
        "resolution_sla_days": 2
    },
    "Safety and Harassment": {
        "department": "Internal Complaints Committee & Anti-Ragging Cell",
        "code": "ICC_SAFETY",
        "email": "safety.redressal@university.edu",
        "escalation_target": "Vice Chancellor & Legal Counsel",
        "resolution_sla_days": 1  # 24 hours mandatory
    },
    "Other": {
        "department": "Office of the Dean of Student Welfare",
        "code": "DSW",
        "email": "dsw@university.edu",
        "escalation_target": "University Ombudsman",
        "resolution_sla_days": 7
    }
}

class RoutingEngine:
    def __init__(self):
        self.routing_map = DEPARTMENT_ROUTING_MAP
        
    def route_grievance(self, category: str, priority: str = "Medium") -> dict:
        info = self.routing_map.get(category, self.routing_map["Other"])
        
        # Priority-adjusted SLA days
        sla_days = info["resolution_sla_days"]
        if priority == "Critical":
            sla_days = max(1, sla_days // 3)
        elif priority == "High":
            sla_days = max(2, sla_days // 2)
            
        escalation_hierarchy = [
            {"level": 1, "authority": info["department"], "role": "Primary Grievance Officer"},
            {"level": 2, "authority": info["escalation_target"], "role": "Escalation Authority"},
            {"level": 3, "authority": "University Grievance Ombudsman", "role": "Final Appellate Body"}
        ]
        
        return {
            "recommended_department": info["department"],
            "department_code": info["code"],
            "official_email": info["email"],
            "target_resolution_days": sla_days,
            "escalation_target": info["escalation_target"],
            "escalation_hierarchy": escalation_hierarchy
        }

routing_engine = RoutingEngine()
