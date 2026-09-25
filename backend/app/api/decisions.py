import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.scenario import ScenarioRecord
from backend.app.models.decision import DecisionLog
from backend.app.models.user import User
from backend.app.models.leaderboard import LeaderboardEntry
from backend.app.models.learner_profile import LearnerProfile
from backend.app.api.auth import get_current_user_optional
from backend.app.game_engine.schemas import DecisionRequest, EvaluationVerdict
from backend.app.game_engine.evaluator import evaluate_decision
from backend.app.api.scenarios import _to_scenario_definition

router = APIRouter(prefix="/api/decisions", tags=["Decisions & Game Engine"])

@router.post("/evaluate", response_model=EvaluationVerdict)
def evaluate_player_choice(
    req: DecisionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    # Retrieve Scenario
    record = db.query(ScenarioRecord).filter(
        ScenarioRecord.scenario_code == req.scenario_code,
        ScenarioRecord.is_active == True
    ).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario '{req.scenario_code}' not found."
        )

    scenario_def = _to_scenario_definition(record)

    # DETERMINISTIC EVALUATION (Zero AI calls)
    verdict: EvaluationVerdict = evaluate_decision(
        scenario=scenario_def,
        chosen_option_id=req.chosen_option_id
    )

    # Persist decision log & update analytics if user is logged in
    if current_user:
        log_entry = DecisionLog(
            user_id=current_user.id,
            scenario_id=record.id,
            chosen_option_id=req.chosen_option_id,
            is_safe=verdict.is_safe,
            score_delta=verdict.score_delta,
            vessel_status=verdict.vessel_status,
            xp_awarded=verdict.xp_awarded,
            rule_feedback=verdict.feedback_rule,
            ai_explanation=None,  # Populated in Phase 3
            tavily_learn_more=None
        )
        db.add(log_entry)

        # Update User XP & Level
        current_user.xp = max(0, current_user.xp + verdict.xp_awarded)
        current_user.level = max(1, (current_user.xp // 250) + 1)

        # Update Leaderboard Entry
        lb = db.query(LeaderboardEntry).filter(LeaderboardEntry.user_id == current_user.id).first()
        if lb:
            lb.total_score = max(0, lb.total_score + verdict.score_delta)
            lb.scenarios_completed += 1
            if verdict.is_safe:
                lb.safe_decisions_count += 1
            if lb.scenarios_completed > 0:
                lb.accuracy_percentage = int((lb.safe_decisions_count / lb.scenarios_completed) * 100)

        # Update Learner Profile topic mastery
        profile = db.query(LearnerProfile).filter(LearnerProfile.user_id == current_user.id).first()
        if profile:
            profile.total_decisions += 1
            delta = 10.0 if verdict.is_safe else -5.0
            
            # Categorical mastery attribution
            if scenario_def.ocean_data.wave_height_m > 2.5 or scenario_def.ocean_data.wind_speed_knots > 25:
                profile.ocean_conditions_mastery = min(100.0, max(0.0, profile.ocean_conditions_mastery + delta))
            if scenario_def.ocean_data.incois_warning_type != "none":
                profile.safety_awareness_mastery = min(100.0, max(0.0, profile.safety_awareness_mastery + delta))
                profile.advisory_compliance_mastery = min(100.0, max(0.0, profile.advisory_compliance_mastery + delta))
            if scenario_def.ocean_data.pfz_zone_active:
                profile.pfz_understanding_mastery = min(100.0, max(0.0, profile.pfz_understanding_mastery + delta))

        db.commit()

    return verdict

from pydantic import BaseModel, Field
from backend.app.ai_service import get_groq_explainer, get_tavily_retriever

class ExplainRequest(BaseModel):
    scenario_code: str
    chosen_option_id: str
    language: str = Field(default="en", description="Language code: en or hi")

class ExplainResponse(BaseModel):
    scenario_code: str
    chosen_option_id: str
    language: str
    explanation: str
    provider: str

class LearnMoreItem(BaseModel):
    title: str
    url: str
    snippet: str
    source: str

class LearnMoreResponse(BaseModel):
    scenario_code: str
    query: str
    provider: str
    results: list[LearnMoreItem]

@router.post("/explain", response_model=ExplainResponse)
def explain_decision_outcome(
    req: ExplainRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    # Retrieve Scenario
    record = db.query(ScenarioRecord).filter(
        ScenarioRecord.scenario_code == req.scenario_code,
        ScenarioRecord.is_active == True
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Scenario '{req.scenario_code}' not found.")

    scenario_def = _to_scenario_definition(record)

    # 1. Deterministic evaluation first
    verdict: EvaluationVerdict = evaluate_decision(
        scenario=scenario_def,
        chosen_option_id=req.chosen_option_id
    )

    # Locate chosen option text
    opt_text = req.chosen_option_id
    for opt in scenario_def.options:
        if opt.id == req.chosen_option_id:
            opt_text = opt.text
            break

    # 2. AI Explanation Layer (Called strictly post-verdict, with graceful fallback)
    explainer = get_groq_explainer()
    explanation_res = explainer.generate_explanation(
        scenario=scenario_def,
        verdict=verdict,
        chosen_option_text=opt_text,
        language=req.language
    )

    # Store in decision log if user logged in
    if current_user:
        latest_log = db.query(DecisionLog).filter(
            DecisionLog.user_id == current_user.id,
            DecisionLog.scenario_id == record.id,
            DecisionLog.chosen_option_id == req.chosen_option_id
        ).order_by(DecisionLog.created_at.desc()).first()
        if latest_log:
            latest_log.ai_explanation = explanation_res["explanation"]
            db.commit()

    return ExplainResponse(
        scenario_code=req.scenario_code,
        chosen_option_id=req.chosen_option_id,
        language=explanation_res["language"],
        explanation=explanation_res["explanation"],
        provider=explanation_res["provider"]
    )

@router.get("/learn-more", response_model=LearnMoreResponse)
def get_authoritative_context(
    scenario_code: str,
    db: Session = Depends(get_db)
):
    record = db.query(ScenarioRecord).filter(
        ScenarioRecord.scenario_code == scenario_code,
        ScenarioRecord.is_active == True
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_code}' not found.")

    query = f"INCOIS ocean advisory guidelines {record.title} {record.location}"
    topic = record.incois_warning_type or "general"
    if record.pfz_zone_active:
        topic = "pfz"

    retriever = get_tavily_retriever()
    search_res = retriever.search_authoritative(query=query, topic=topic, max_results=3)

    return LearnMoreResponse(
        scenario_code=scenario_code,
        query=search_res["query"],
        provider=search_res["provider"],
        results=[LearnMoreItem(**item) for item in search_res["results"]]
    )
