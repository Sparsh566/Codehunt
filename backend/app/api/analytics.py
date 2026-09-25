import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.learner_profile import LearnerProfile
from backend.app.models.decision import DecisionLog
from backend.app.models.scenario import ScenarioRecord
from backend.app.models.leaderboard import LeaderboardEntry
from backend.app.api.auth import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Learning Analytics & Gamification"])

BADGES_CATALOG = [
    {
        "id": "welcome_sailor",
        "name": "First Voyage",
        "icon": "⚓",
        "description": "Registered and set sail on Codehunt v2",
        "category": "milestone"
    },
    {
        "id": "quiz_scholar",
        "name": "Ocean Scholar",
        "icon": "📖",
        "description": "Scored over 80% on the Ocean Literacy curriculum quiz",
        "category": "literacy"
    },
    {
        "id": "high_wave_guardian",
        "name": "Wave Master",
        "icon": "🌊",
        "description": "Successfully complied with an INCOIS Orange/Red High Wave alert",
        "category": "safety"
    },
    {
        "id": "pfz_navigator",
        "name": "PFZ Navigator",
        "icon": "🐟",
        "description": "Exploited an active Potential Fishing Zone thermal front safely",
        "category": "harvest"
    },
    {
        "id": "cyclone_survivor",
        "name": "Cyclone Survivor",
        "icon": "🌀",
        "description": "Executed a successful deep-sea storm track diversion",
        "category": "navigation"
    },
    {
        "id": "pirate_legend",
        "name": "King of the Seas",
        "icon": "🏴‍☠️",
        "description": "Escaped treacherous rip currents and navigated coral atoll labyrinths",
        "category": "adventure"
    },
    {
        "id": "streak_veteran",
        "name": "Veteran Navigator",
        "icon": "🔥",
        "description": "Maintained a 5-day maritime decision streak",
        "category": "streak"
    }
]

class BadgeItem(BaseModel):
    id: str
    name: str
    icon: str
    description: str
    category: str
    is_unlocked: bool

class MasteryMetrics(BaseModel):
    ocean_conditions_mastery: float
    safety_awareness_mastery: float
    pfz_understanding_mastery: float
    advisory_compliance_mastery: float
    overall_literacy_index: float

class VoyageHistoryItem(BaseModel):
    decision_id: int
    scenario_code: str
    scenario_title: str
    role: str
    is_safe: bool
    score_delta: int
    xp_awarded: int
    vessel_status: str
    rule_feedback: Optional[str]
    created_at: str

class LearnerProfileResponse(BaseModel):
    user_id: int
    username: str
    role: str
    level: int
    xp: int
    xp_for_next_level: int
    current_streak: int
    total_decisions: int
    quiz_attempts: int
    quiz_high_score: int
    global_rank: int
    mastery: MasteryMetrics
    badges: List[BadgeItem]
    recent_voyages: List[VoyageHistoryItem]

@router.get("/badges", response_model=List[Dict[str, Any]])
def list_badge_catalog():
    return BADGES_CATALOG

@router.get("/profile", response_model=LearnerProfileResponse)
def get_learner_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == current_user.id).first()
    if not profile:
        profile = LearnerProfile(
            user_id=current_user.id,
            ocean_conditions_mastery=0.0,
            safety_awareness_mastery=0.0,
            pfz_understanding_mastery=0.0,
            advisory_compliance_mastery=0.0,
            total_decisions=0,
            quiz_attempts=0,
            quiz_high_score=0
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    # Leaderboard rank
    higher_count = db.query(LeaderboardEntry).filter(
        LeaderboardEntry.total_score > (
            db.query(LeaderboardEntry.total_score).filter(LeaderboardEntry.user_id == current_user.id).scalar() or 0
        )
    ).count()
    global_rank = higher_count + 1

    # Unlocked badges parsing
    try:
        user_badge_ids = set(json.loads(current_user.badges or "[]"))
    except Exception:
        user_badge_ids = {"welcome_sailor"}

    # Dynamic badge unlock evaluation based on gameplay progress
    if profile.quiz_high_score >= 80:
        user_badge_ids.add("quiz_scholar")
    if profile.safety_awareness_mastery >= 60:
        user_badge_ids.add("high_wave_guardian")
    if profile.pfz_understanding_mastery >= 50:
        user_badge_ids.add("pfz_navigator")
    if current_user.role == "pirate_king" and profile.total_decisions >= 2:
        user_badge_ids.add("pirate_legend")
    if current_user.current_streak >= 5:
        user_badge_ids.add("streak_veteran")

    current_user.badges = json.dumps(list(user_badge_ids))
    db.commit()

    badges_list = []
    for b in BADGES_CATALOG:
        badges_list.append(BadgeItem(
            id=b["id"],
            name=b["name"],
            icon=b["icon"],
            description=b["description"],
            category=b["category"],
            is_unlocked=(b["id"] in user_badge_ids)
        ))

    # Overall literacy index
    overall_index = round(
        (profile.ocean_conditions_mastery +
         profile.safety_awareness_mastery +
         profile.pfz_understanding_mastery +
         profile.advisory_compliance_mastery) / 4.0, 1
    )

    # Recent decisions history
    logs = (
        db.query(DecisionLog, ScenarioRecord)
        .join(ScenarioRecord, DecisionLog.scenario_id == ScenarioRecord.id)
        .filter(DecisionLog.user_id == current_user.id)
        .order_by(desc(DecisionLog.created_at))
        .limit(10)
        .all()
    )

    voyages = []
    for log, sc in logs:
        voyages.append(VoyageHistoryItem(
            decision_id=log.id,
            scenario_code=sc.scenario_code,
            scenario_title=sc.title,
            role=sc.role,
            is_safe=log.is_safe,
            score_delta=log.score_delta,
            xp_awarded=log.xp_awarded,
            vessel_status=log.vessel_status or "Intact",
            rule_feedback=log.rule_feedback,
            created_at=log.created_at.strftime("%Y-%m-%d %H:%M UTC") if log.created_at else ""
        ))

    xp_next = (current_user.level) * 250

    return LearnerProfileResponse(
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        level=current_user.level,
        xp=current_user.xp,
        xp_for_next_level=xp_next,
        current_streak=current_user.current_streak,
        total_decisions=profile.total_decisions,
        quiz_attempts=profile.quiz_attempts,
        quiz_high_score=profile.quiz_high_score,
        global_rank=global_rank,
        mastery=MasteryMetrics(
            ocean_conditions_mastery=round(profile.ocean_conditions_mastery, 1),
            safety_awareness_mastery=round(profile.safety_awareness_mastery, 1),
            pfz_understanding_mastery=round(profile.pfz_understanding_mastery, 1),
            advisory_compliance_mastery=round(profile.advisory_compliance_mastery, 1),
            overall_literacy_index=overall_index
        ),
        badges=badges_list,
        recent_voyages=voyages
    )
