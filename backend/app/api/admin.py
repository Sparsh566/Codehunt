import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.models.scenario import ScenarioRecord
from backend.app.models.decision import DecisionLog
from backend.app.models.learner_profile import LearnerProfile
from backend.app.api.auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["Admin Operations"])

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not (current_user.is_admin or current_user.role == "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required to access this operational console."
        )
    return current_user

class ScenarioOptionItem(BaseModel):
    id: str
    text: str
    risk_level: str
    fuel_cost: Optional[int] = 15
    catch_potential: Optional[str] = "Normal"

class ScenarioPayload(BaseModel):
    scenario_code: str
    role: str
    title: str
    location: str
    narrative: str
    wave_height_m: float
    wind_speed_knots: float
    swell_period_sec: Optional[float] = 10.0
    sea_surface_temp_c: Optional[float] = 28.0
    pfz_zone_active: Optional[bool] = False
    incois_warning_type: Optional[str] = "none"
    incois_alert_level: Optional[str] = "GREEN"
    options: List[Dict[str, Any]]
    recommended_action_id: str
    consequences: Dict[str, Dict[str, Any]]
    is_active: Optional[bool] = True

class ScenarioDetailResponse(BaseModel):
    id: int
    scenario_code: str
    role: str
    title: str
    location: str
    narrative: str
    wave_height_m: float
    wind_speed_knots: float
    swell_period_sec: float
    sea_surface_temp_c: float
    pfz_zone_active: bool
    incois_warning_type: str
    incois_alert_level: str
    options: List[Dict[str, Any]]
    recommended_action_id: str
    consequences: Dict[str, Any]
    is_active: bool

class AdminStatsResponse(BaseModel):
    total_users: int
    total_decisions: int
    safe_decisions: int
    dangerous_decisions: int
    safety_rate_pct: float
    active_scenarios_count: int
    role_distribution: Dict[str, int]
    common_misconceptions: List[Dict[str, Any]]
    scenario_risk_analysis: List[Dict[str, Any]]

@router.get("/stats", response_model=AdminStatsResponse)
def get_system_analytics(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_decisions = db.query(DecisionLog).count()
    safe_decisions = db.query(DecisionLog).filter(DecisionLog.is_safe == True).count()
    dangerous_decisions = total_decisions - safe_decisions
    safety_rate = round((safe_decisions / total_decisions * 100), 1) if total_decisions > 0 else 100.0
    active_scenarios = db.query(ScenarioRecord).filter(ScenarioRecord.is_active == True).count()

    # Role breakdown in DecisionLogs
    roles = ["fisherman", "ship_captain", "pirate_king"]
    role_dist = {}
    for r in roles:
        c = (
            db.query(DecisionLog)
            .join(ScenarioRecord, DecisionLog.scenario_id == ScenarioRecord.id)
            .filter(ScenarioRecord.role == r)
            .count()
        )
        role_dist[r] = c

    # Scenario risk analysis: failure count per scenario
    scenarios = db.query(ScenarioRecord).all()
    risk_analysis = []
    for sc in scenarios:
        sc_total = db.query(DecisionLog).filter(DecisionLog.scenario_id == sc.id).count()
        sc_unsafe = db.query(DecisionLog).filter(DecisionLog.scenario_id == sc.id, DecisionLog.is_safe == False).count()
        fail_pct = round((sc_unsafe / sc_total * 100), 1) if sc_total > 0 else 0.0
        risk_analysis.append({
            "scenario_id": sc.id,
            "scenario_code": sc.scenario_code,
            "title": sc.title,
            "role": sc.role,
            "total_attempts": sc_total,
            "unsafe_decisions": sc_unsafe,
            "failure_rate_pct": fail_pct,
            "alert_level": sc.incois_alert_level
        })

    risk_analysis.sort(key=lambda x: x["failure_rate_pct"], reverse=True)

    # Top common misconceptions (unsafe choices with rule feedback)
    unsafe_logs = (
        db.query(DecisionLog.chosen_option_id, DecisionLog.rule_feedback, func.count(DecisionLog.id).label("count"))
        .filter(DecisionLog.is_safe == False)
        .group_by(DecisionLog.chosen_option_id, DecisionLog.rule_feedback)
        .order_by(desc("count"))
        .limit(5)
        .all()
    )

    misconceptions = [
        {
            "chosen_option": log[0],
            "feedback": log[1] or "Violated maritime safety standard",
            "occurrences": log[2]
        }
        for log in unsafe_logs
    ]

    return AdminStatsResponse(
        total_users=total_users,
        total_decisions=total_decisions,
        safe_decisions=safe_decisions,
        dangerous_decisions=dangerous_decisions,
        safety_rate_pct=safety_rate,
        active_scenarios_count=active_scenarios,
        role_distribution=role_dist,
        common_misconceptions=misconceptions,
        scenario_risk_analysis=risk_analysis
    )

@router.get("/scenarios", response_model=List[ScenarioDetailResponse])
def list_admin_scenarios(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    scenarios = db.query(ScenarioRecord).order_by(ScenarioRecord.id).all()
    results = []
    for sc in scenarios:
        results.append(ScenarioDetailResponse(
            id=sc.id,
            scenario_code=sc.scenario_code,
            role=sc.role,
            title=sc.title,
            location=sc.location,
            narrative=sc.narrative,
            wave_height_m=sc.wave_height_m,
            wind_speed_knots=sc.wind_speed_knots,
            swell_period_sec=sc.swell_period_sec,
            sea_surface_temp_c=sc.sea_surface_temp_c,
            pfz_zone_active=sc.pfz_zone_active,
            incois_warning_type=sc.incois_warning_type,
            incois_alert_level=sc.incois_alert_level,
            options=json.loads(sc.options_json),
            recommended_action_id=sc.recommended_action_id,
            consequences=json.loads(sc.consequences_json),
            is_active=sc.is_active
        ))
    return results

@router.post("/scenarios", response_model=ScenarioDetailResponse)
def create_scenario(
    payload: ScenarioPayload,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(ScenarioRecord).filter(ScenarioRecord.scenario_code == payload.scenario_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scenario code '{payload.scenario_code}' already exists."
        )

    sc = ScenarioRecord(
        scenario_code=payload.scenario_code,
        role=payload.role,
        title=payload.title,
        location=payload.location,
        narrative=payload.narrative,
        wave_height_m=payload.wave_height_m,
        wind_speed_knots=payload.wind_speed_knots,
        swell_period_sec=payload.swell_period_sec,
        sea_surface_temp_c=payload.sea_surface_temp_c,
        pfz_zone_active=payload.pfz_zone_active,
        incois_warning_type=payload.incois_warning_type,
        incois_alert_level=payload.incois_alert_level,
        options_json=json.dumps(payload.options),
        recommended_action_id=payload.recommended_action_id,
        consequences_json=json.dumps(payload.consequences),
        is_active=payload.is_active
    )
    db.add(sc)
    db.commit()
    db.refresh(sc)

    return ScenarioDetailResponse(
        id=sc.id,
        scenario_code=sc.scenario_code,
        role=sc.role,
        title=sc.title,
        location=sc.location,
        narrative=sc.narrative,
        wave_height_m=sc.wave_height_m,
        wind_speed_knots=sc.wind_speed_knots,
        swell_period_sec=sc.swell_period_sec,
        sea_surface_temp_c=sc.sea_surface_temp_c,
        pfz_zone_active=sc.pfz_zone_active,
        incois_warning_type=sc.incois_warning_type,
        incois_alert_level=sc.incois_alert_level,
        options=json.loads(sc.options_json),
        recommended_action_id=sc.recommended_action_id,
        consequences=json.loads(sc.consequences_json),
        is_active=sc.is_active
    )

@router.put("/scenarios/{scenario_id}", response_model=ScenarioDetailResponse)
def update_scenario(
    scenario_id: int,
    payload: ScenarioPayload,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    sc = db.query(ScenarioRecord).filter(ScenarioRecord.id == scenario_id).first()
    if not sc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID {scenario_id} not found."
        )

    sc.role = payload.role
    sc.title = payload.title
    sc.location = payload.location
    sc.narrative = payload.narrative
    sc.wave_height_m = payload.wave_height_m
    sc.wind_speed_knots = payload.wind_speed_knots
    sc.swell_period_sec = payload.swell_period_sec
    sc.sea_surface_temp_c = payload.sea_surface_temp_c
    sc.pfz_zone_active = payload.pfz_zone_active
    sc.incois_warning_type = payload.incois_warning_type
    sc.incois_alert_level = payload.incois_alert_level
    sc.options_json = json.dumps(payload.options)
    sc.recommended_action_id = payload.recommended_action_id
    sc.consequences_json = json.dumps(payload.consequences)
    sc.is_active = payload.is_active

    db.commit()
    db.refresh(sc)

    return ScenarioDetailResponse(
        id=sc.id,
        scenario_code=sc.scenario_code,
        role=sc.role,
        title=sc.title,
        location=sc.location,
        narrative=sc.narrative,
        wave_height_m=sc.wave_height_m,
        wind_speed_knots=sc.wind_speed_knots,
        swell_period_sec=sc.swell_period_sec,
        sea_surface_temp_c=sc.sea_surface_temp_c,
        pfz_zone_active=sc.pfz_zone_active,
        incois_warning_type=sc.incois_warning_type,
        incois_alert_level=sc.incois_alert_level,
        options=json.loads(sc.options_json),
        recommended_action_id=sc.recommended_action_id,
        consequences=json.loads(sc.consequences_json),
        is_active=sc.is_active
    )

@router.delete("/scenarios/{scenario_id}")
def delete_scenario(
    scenario_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    sc = db.query(ScenarioRecord).filter(ScenarioRecord.id == scenario_id).first()
    if not sc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID {scenario_id} not found."
        )

    # Soft delete
    sc.is_active = False
    db.commit()
    return {"message": f"Scenario '{sc.scenario_code}' archived successfully."}

@router.post("/scenarios/{scenario_id}/toggle")
def toggle_scenario_active(
    scenario_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    sc = db.query(ScenarioRecord).filter(ScenarioRecord.id == scenario_id).first()
    if not sc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario with ID {scenario_id} not found."
        )

    sc.is_active = not sc.is_active
    db.commit()
    return {"message": f"Scenario '{sc.scenario_code}' active status is now {sc.is_active}."}
