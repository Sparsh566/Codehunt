from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class OceanConditions(BaseModel):
    wave_height_m: float = Field(..., description="Significant wave height in meters")
    wind_speed_knots: float = Field(..., description="Sustained wind speed in knots")
    swell_period_sec: float = Field(default=10.0, description="Dominant swell wave period in seconds")
    sea_surface_temp_c: float = Field(default=28.0, description="Sea surface temperature in Celsius")
    pfz_zone_active: bool = Field(default=False, description="Whether a Potential Fishing Zone is detected")
    incois_warning_type: str = Field(default="none", description="Alert type: none, high_wave, rough_sea, cyclone, tsunami, rip_current")
    incois_alert_level: str = Field(default="GREEN", description="Color code: GREEN, YELLOW, ORANGE, RED")

class ScenarioOption(BaseModel):
    id: str = Field(..., description="Unique option identifier, e.g., opt_return_harbor")
    text: str = Field(..., description="Player-facing action choice description")
    action_type: str = Field(..., description="Action classification, e.g., safe_shelter, high_risk_harvest, storm_diversion")

class ConsequenceRule(BaseModel):
    is_safe: bool = Field(..., description="Whether action complies with maritime safety")
    score_delta: int = Field(..., description="Score change (positive for safe/optimal, negative for dangerous)")
    vessel_status: str = Field(default="Intact", description="Condition of vessel/gear: Intact, Strained, Damaged, Capsized")
    xp_awarded: int = Field(default=0, description="XP awarded towards level advancement")
    feedback_rule: str = Field(..., description="Deterministic educational rule explaining the physical outcome")
    resource_impact: Dict[str, Any] = Field(
        default_factory=lambda: {"fuel_burn": "moderate", "catch_yield": "none", "crew_morale": "normal"},
        description="Detailed maritime resource changes"
    )

class ScenarioDefinition(BaseModel):
    scenario_code: str
    role: str  # fisherman, ship_captain, tourism_operator
    title: str
    location: str
    narrative: str
    ocean_data: OceanConditions
    options: List[ScenarioOption]
    recommended_action_id: str
    consequences: Dict[str, ConsequenceRule]

class DecisionRequest(BaseModel):
    scenario_code: str
    chosen_option_id: str

class EvaluationVerdict(BaseModel):
    scenario_code: str
    chosen_option_id: str
    recommended_action_id: str
    is_safe: bool
    is_optimal: bool
    score_delta: int
    xp_awarded: int
    vessel_status: str
    feedback_rule: str
    resource_impact: Dict[str, Any]
    ocean_context: OceanConditions
