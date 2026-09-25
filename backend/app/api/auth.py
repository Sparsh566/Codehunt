import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.leaderboard import LeaderboardEntry
from backend.app.models.learner_profile import LearnerProfile
from backend.app.utils.security import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    role: Optional[str] = "learner"

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    role: str
    xp: int
    level: int
    current_streak: int
    is_admin: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    if not credentials:
        return None
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

@router.post("/register", response_model=TokenResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    clean_username = req.username.strip()
    if len(clean_username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(req.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters")

    existing_user = db.query(User).filter(User.username == clean_username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists. Please choose another.")
    
    if req.email:
        existing_email = db.query(User).filter(User.email == req.email.strip()).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email is already registered.")

    new_user = User(
        username=clean_username,
        email=req.email.strip() if req.email else None,
        hashed_password=hash_password(req.password),
        role=req.role or "learner",
        xp=0,
        level=1,
        current_streak=1,
        badges=json.dumps(["welcome_sailor"])
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize Leaderboard Entry
    lb_entry = LeaderboardEntry(
        user_id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        total_score=0,
        scenarios_completed=0,
        safe_decisions_count=0,
        accuracy_percentage=0,
        rank=0
    )
    db.add(lb_entry)

    # Initialize Learner Profile
    learner_profile = LearnerProfile(
        user_id=new_user.id,
        ocean_conditions_mastery=0.0,
        safety_awareness_mastery=0.0,
        pfz_understanding_mastery=0.0,
        advisory_compliance_mastery=0.0,
        total_decisions=0,
        quiz_attempts=0,
        quiz_high_score=0
    )
    db.add(learner_profile)
    db.commit()

    token = create_access_token({"sub": str(new_user.id), "username": new_user.username})
    user_resp = UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        xp=new_user.xp,
        level=new_user.level,
        current_streak=new_user.current_streak,
        is_admin=new_user.is_admin
    )
    return TokenResponse(access_token=token, user=user_resp)

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    clean_username = req.username.strip()
    user = db.query(User).filter(User.username == clean_username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token({"sub": str(user.id), "username": user.username})
    user_resp = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        xp=user.xp,
        level=user.level,
        current_streak=user.current_streak,
        is_admin=user.is_admin
    )
    return TokenResponse(access_token=token, user=user_resp)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        xp=current_user.xp,
        level=current_user.level,
        current_streak=current_user.current_streak,
        is_admin=current_user.is_admin
    )
