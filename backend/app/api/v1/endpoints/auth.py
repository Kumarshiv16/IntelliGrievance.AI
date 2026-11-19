"""
IntelliGrievance AI - Authentication Endpoints
Handles registration, login, JWT issuance, profile retrieval, and demo credentials.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.core.security import hash_password, verify_password, create_access_token
from backend.app.models.entities import User, StudentProfile, AuditLog
from backend.app.schemas.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
def register_user(req: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == req.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
        
    hashed = hash_password(req.password)
    user = User(
        email=req.email.lower(),
        hashed_password=hashed,
        full_name=req.full_name,
        role=req.role,
        department_code=req.department_code
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    if req.role == "student":
        roll_no = req.roll_number or f"STU-{user.id + 21000}"
        profile = StudentProfile(
            user_id=user.id,
            roll_number=roll_no,
            department=req.academic_department or "Computer Science and Engineering",
            academic_year=req.academic_year or "3rd Year",
            hostel_block=req.hostel_block or "Hostel Block A",
            phone_number=req.phone_number
        )
        db.add(profile)
        db.commit()
        
    token = create_access_token({"sub": str(user.id), "role": user.role, "email": user.email})
    
    # Audit log
    audit = AuditLog(actor_id=user.id, actor_email=user.email, action="USER_REGISTERED", resource_type="USER", resource_id=str(user.id))
    db.add(audit)
    db.commit()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "department_code": user.department_code
        }
    }

@router.post("/login", response_model=TokenResponse)
def login_user(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )
        
    token = create_access_token({"sub": str(user.id), "role": user.role, "email": user.email})
    
    audit = AuditLog(actor_id=user.id, actor_email=user.email, action="USER_LOGIN", resource_type="USER", resource_id=str(user.id))
    db.add(audit)
    db.commit()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "department_code": user.department_code
        }
    }

@router.get("/me")
def get_current_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile_data = None
    if current_user.role == "student" and current_user.profile:
        p = current_user.profile
        profile_data = {
            "roll_number": p.roll_number,
            "department": p.department,
            "academic_year": p.academic_year,
            "hostel_block": p.hostel_block,
            "phone_number": p.phone_number
        }
        
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "department_code": current_user.department_code,
        "profile": profile_data
    }
