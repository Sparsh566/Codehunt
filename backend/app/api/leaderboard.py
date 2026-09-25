from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.session import get_db
from backend.app.models.leaderboard import LeaderboardEntry
from backend.app.models.user import User
from backend.app.api.auth import get_current_user_optional

router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])

class LeaderboardItem(BaseModel):
    rank: int
    user_id: int
    username: str
    role: str
    total_score: int
    scenarios_completed: int
    safe_decisions_count: int
    accuracy_percentage: int

@router.get("", response_model=List[LeaderboardItem])
def get_leaderboard(
    role: Optional[str] = Query(None, description="Filter by role: fisherman, ship_captain, pirate_king"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(LeaderboardEntry)
    if role and role != "all":
        query = query.filter(LeaderboardEntry.role == role.strip().lower())
    
    entries = query.order_by(desc(LeaderboardEntry.total_score)).limit(limit).all()

    items = []
    for idx, e in enumerate(entries, start=1):
        items.append(LeaderboardItem(
            rank=idx,
            user_id=e.user_id,
            username=e.username,
            role=e.role,
            total_score=e.total_score,
            scenarios_completed=e.scenarios_completed,
            safe_decisions_count=e.safe_decisions_count,
            accuracy_percentage=e.accuracy_percentage
        ))
    return items

@router.get("/me", response_model=Optional[LeaderboardItem])
def get_my_leaderboard_entry(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    if not current_user:
        return None
    
    entry = db.query(LeaderboardEntry).filter(LeaderboardEntry.user_id == current_user.id).first()
    if not entry:
        return None
    
    # Calculate rank dynamically
    higher_count = db.query(LeaderboardEntry).filter(LeaderboardEntry.total_score > entry.total_score).count()
    return LeaderboardItem(
        rank=higher_count + 1,
        user_id=entry.user_id,
        username=entry.username,
        role=entry.role,
        total_score=entry.total_score,
        scenarios_completed=entry.scenarios_completed,
        safe_decisions_count=entry.safe_decisions_count,
        accuracy_percentage=entry.accuracy_percentage
    )
