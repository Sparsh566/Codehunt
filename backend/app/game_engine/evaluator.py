"""Deterministic Game Engine Evaluator.

Pure rule-based evaluation logic for ocean decision scenarios.
ZERO LLM / AI dependencies. Fully idempotent and unit-testable.
"""

from typing import Optional
from backend.app.game_engine.schemas import (
    ScenarioDefinition,
    EvaluationVerdict,
    ConsequenceRule,
)
from backend.app.game_engine.rules import check_role_safety_thresholds

def evaluate_decision(
    scenario: ScenarioDefinition,
    chosen_option_id: str
) -> EvaluationVerdict:
    """Evaluates a player's action deterministically based on maritime laws and INCOIS thresholds.

    Parameters:
        scenario: The full scenario context with ocean parameters and consequence matrix.
        chosen_option_id: The ID of the option selected by the player.

    Returns:
        EvaluationVerdict: The deterministic verdict with safety status, score deltas,
                           vessel status, and educational feedback.
    """
    chosen_rule: Optional[ConsequenceRule] = scenario.consequences.get(chosen_option_id)
    is_optimal = (chosen_option_id == scenario.recommended_action_id)

    if not chosen_rule:
        # Fallback if unknown option was passed
        return EvaluationVerdict(
            scenario_code=scenario.scenario_code,
            chosen_option_id=chosen_option_id,
            recommended_action_id=scenario.recommended_action_id,
            is_safe=False,
            is_optimal=False,
            score_delta=-50,
            xp_awarded=0,
            vessel_status="Unknown Action Disruption",
            feedback_rule="Selected action could not be verified by the maritime safety matrix.",
            resource_impact={"fuel_burn": "wasted", "catch_yield": "none"},
            ocean_context=scenario.ocean_data
        )

    # Cross-verify with environmental thresholds
    safety_check = check_role_safety_thresholds(
        role=scenario.role,
        wave_height_m=scenario.ocean_data.wave_height_m,
        wind_speed_knots=scenario.ocean_data.wind_speed_knots,
        incois_alert_level=scenario.ocean_data.incois_alert_level
    )

    is_safe = chosen_rule.is_safe
    score_delta = chosen_rule.score_delta
    xp_awarded = chosen_rule.xp_awarded
    vessel_status = chosen_rule.vessel_status
    feedback = chosen_rule.feedback_rule

    # If the user chose an unsafe action in hazardous conditions, ensure penalty is enforced
    if safety_check["is_inherently_hazardous"] and not is_safe:
        # Guarantee score penalty is negative
        if score_delta > 0:
            score_delta = -score_delta

    return EvaluationVerdict(
        scenario_code=scenario.scenario_code,
        chosen_option_id=chosen_option_id,
        recommended_action_id=scenario.recommended_action_id,
        is_safe=is_safe,
        is_optimal=is_optimal,
        score_delta=score_delta,
        xp_awarded=xp_awarded,
        vessel_status=vessel_status,
        feedback_rule=feedback,
        resource_impact=chosen_rule.resource_impact,
        ocean_context=scenario.ocean_data
    )
