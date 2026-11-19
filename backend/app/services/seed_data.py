"""
IntelliGrievance AI - Database Seeder Script
Initializes institutional departments and seeds realistic demo grievances
spanning various categories, priorities, statuses, and timeline distributions.
Ensures students, administrators, and department heads have immediate demo data.
"""

import os
import sys
import random
import datetime
from sqlalchemy.orm import Session

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.app.core.database import SessionLocal, engine, Base
from backend.app.core.security import hash_password
from backend.app.models.entities import User, StudentProfile, Department, Grievance, GrievancePrediction, GrievanceStatusHistory
from backend.app.ml.category_classifier import category_engine
from backend.app.ml.severity_predictor import severity_engine
from backend.app.ml.routing_engine import routing_engine, DEPARTMENT_ROUTING_MAP
from backend.app.ml.explainability import explainability_engine

DEMO_USERS = [
    # Admin
    {"email": "admin@university.edu", "full_name": "Dr. Sarah Jenkins (Registrar)", "role": "admin", "password": "AdminPassword123!"},
    # Department Heads
    {"email": "coe.head@university.edu", "full_name": "Prof. R. Narayanan (Controller of Exams)", "role": "department_head", "department_code": "COE", "password": "DeptPassword123!"},
    {"email": "warden.head@university.edu", "full_name": "Col. V. Sharma (Chief Warden)", "role": "department_head", "department_code": "HOSTEL", "password": "DeptPassword123!"},
    {"email": "acad.head@university.edu", "full_name": "Dr. Meenakshi Sundaram (Dean Academics)", "role": "department_head", "department_code": "ACAD", "password": "DeptPassword123!"},
    # Students
    {"email": "student@university.edu", "full_name": "Aarav Sharma", "role": "student", "roll_number": "22CSE104", "password": "StudentPassword123!"},
    {"email": "priya.patel@university.edu", "full_name": "Priya Patel", "role": "student", "roll_number": "22AIML045", "password": "StudentPassword123!"},
    {"email": "rohit.verma@university.edu", "full_name": "Rohit Verma", "role": "student", "roll_number": "21ECE088", "password": "StudentPassword123!"}
]

SAMPLE_GRIEVANCE_SEEDS = [
    ("Urgent: Admit card hall ticket not generated on portal and semester exam starts tomorrow morning 9 AM.", "Hall Ticket Portal Failure", "Exam Hall 3"),
    ("Severe water shortage in Hostel Block C for past 4 days, taps are completely dry and students cannot bathe.", "Hostel C Water Emergency", "Hostel Block C"),
    ("Senior students brutally ragging 1st year freshers in Hostel Block A room 405 at 1 AM, forcing abusive tasks.", "Ragging Incident in Hostel A", "Hostel Block A"),
    ("College bus on Route 7 driving extremely rashly at 90 km/h, nearly collided with truck on highway.", "Reckless Bus Driving", "Campus Route 7 Bus"),
    ("Lab practical machines in Computing Lab 4 lack required compilers and GPUs, practical assignments cannot be run.", "Lab 4 GPU & Compiler Failure", "Computing Lab 4"),
    ("Government scholarship credited to college account has not been disbursed to student for past 7 months.", "Scholarship Disbursal Delay", "Main Administrative Block"),
    ("Bonafide certificate needed for passport interview on Friday pending at Registrar counter for 3 weeks.", "Delayed Bonafide Certificate", "Main Administrative Block"),
    ("Elevator in Science Block plunged one floor and jammed with 6 students stuck inside with no alarm.", "Science Block Elevator Plunge", "Science Block"),
    ("Prescribed textbook for core curriculum has only 2 copies in Central Library 2nd Floor for 240 students.", "Severe Textbook Shortage", "Central Library 2nd Floor"),
    ("University student ERP crashed on semester subject registration day, students cannot register.", "ERP Registration Portal Crash", "Computing Lab 4"),
    ("Assistant professor using abusive language and passing derogatory remarks in classroom.", "Abusive Faculty Conduct", "Department Seminar Hall"),
    ("Canteen food prices increased by 50% without student committee notice and food hygiene is poor.", "Canteen Overcharging & Hygiene", "North Canteen"),
    ("Geyser in bathroom Hostel Block B sparking with burning plastic smell, risk of electrical shock.", "Geyser Spark Hazard", "Hostel Block B"),
    ("Live electrical wire hanging openly from ceiling near staircase of Auditorium Complex, severe hazard.", "Naked Live Electrical Wire", "Auditorium Complex"),
    ("Two-wheeler parking attendant demanding illegal parking fee inside university premises.", "Illegal Parking Charges", "General Campus"),
    ("Classroom projector and audio system in Hostel Block C not working during seminar presentations.", "Audio Projector Malfunction", "Hostel Block C"),
    ("Exam hall 3 had severe power outage and no emergency lighting during 3-hour exam.", "Exam Hall Power Outage", "Exam Hall 3"),
    ("Wi-Fi connectivity in Hostel Block C is completely dead for the past 5 days, cannot submit assignments.", "Hostel C Wi-Fi Outage", "Hostel Block C")
]

def seed_database():
    print("Creating all database tables...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    
    # 1. Seed Departments
    if db.query(Department).count() == 0:
        print("Seeding institutional departments...")
        for cat, info in DEPARTMENT_ROUTING_MAP.items():
            dept = Department(
                code=info["code"],
                name=info["department"],
                contact_email=info["email"],
                escalation_target=info["escalation_target"],
                default_sla_hours=info["resolution_sla_days"] * 24,
                is_active=True
            )
            db.add(dept)
        db.commit()
        
    # 2. Seed Users
    seeded_users = {}
    for u in DEMO_USERS:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user = User(
                email=u["email"],
                hashed_password=hash_password(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
                department_code=u.get("department_code")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            if u["role"] == "student":
                profile = StudentProfile(
                    user_id=user.id,
                    roll_number=u["roll_number"],
                    department="Computer Science and Engineering",
                    academic_year="3rd Year (BTech)",
                    hostel_block="Hostel Block C",
                    phone_number="+91 98765 43210"
                )
                db.add(profile)
                db.commit()
            seeded_users[u["email"]] = user
        else:
            seeded_users[u["email"]] = existing
            
    # 3. Seed Demo Grievances
    if db.query(Grievance).count() < 10:
        print("Seeding realistic demo grievances with AI predictions...")
        students = [u for u in seeded_users.values() if u.role == "student"]
        
        statuses = ["Submitted", "Under Review", "Assigned", "In Progress", "Resolved"]
        status_weights = [0.15, 0.20, 0.20, 0.25, 0.20]
        
        for idx, (desc, title, loc) in enumerate(SAMPLE_GRIEVANCE_SEEDS, 1):
            student = random.choice(students)
            
            # Predict
            cat_res = category_engine.predict(desc)
            cat = cat_res["category"]
            sev_res = severity_engine.predict(desc, predicted_category=cat)
            pri = sev_res["priority"]
            route = routing_engine.route_grievance(cat, pri)
            
            # Random status
            st = random.choices(statuses, weights=status_weights)[0]
            
            # Date distribution over past 14 days
            days_ago = random.randint(0, 13)
            hours_ago = random.randint(1, 23)
            created_at = datetime.datetime.utcnow() - datetime.timedelta(days=days_ago, hours=hours_ago)
            resolved_at = (created_at + datetime.timedelta(hours=random.randint(12, 72))) if st == "Resolved" else None
            
            ticket_id = f"TKT-2026-{idx:05d}"
            g = Grievance(
                ticket_id=ticket_id,
                student_id=student.id,
                title=title,
                description=desc,
                location=loc,
                category=cat,
                confidence=cat_res["confidence"],
                priority=pri,
                severity_score=sev_res["severity_score"],
                sla_hours=sev_res["sla_hours"],
                department_code=route["department_code"],
                assigned_department=route["recommended_department"],
                status=st,
                is_safeguard_override=sev_res["safeguard_override"],
                is_potential_duplicate=False,
                created_at=created_at,
                resolved_at=resolved_at,
                resolution_notes="Issue inspected and resolved by campus engineering team." if st == "Resolved" else None
            )
            db.add(g)
            db.commit()
            db.refresh(g)
            
            # Snapshot & history
            history = GrievanceStatusHistory(
                grievance_id=g.id,
                from_status=None,
                to_status=st,
                changed_by_user="System AI Dispatcher",
                remarks=f"Initial ingestion and classification to {cat} / {pri}.",
                created_at=created_at
            )
            db.add(history)
            db.commit()
            
        print(f"Database successfully seeded! {len(SAMPLE_GRIEVANCE_SEEDS)} grievances loaded.")
    db.close()

if __name__ == "__main__":
    seed_database()
