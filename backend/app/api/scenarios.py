import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.models.scenario import ScenarioRecord
from backend.app.game_engine.schemas import ScenarioDefinition, OceanConditions, ScenarioOption
from backend.app.ocean_adapter import get_ocean_provider
from backend.app.ocean_adapter.models import INCOISTelemetrySnapshot, INCOISStation

router = APIRouter(prefix="/api/scenarios", tags=["Scenarios & Ocean Telemetry"])

def _to_scenario_definition(record: ScenarioRecord) -> ScenarioDefinition:
    try:
        opts = [ScenarioOption(**o) for o in json.loads(record.options_json)]
    except Exception:
        opts = []
    try:
        cons = json.loads(record.consequences_json)
    except Exception:
        cons = {}

    ocean_data = OceanConditions(
        wave_height_m=record.wave_height_m,
        wind_speed_knots=record.wind_speed_knots,
        swell_period_sec=record.swell_period_sec,
        sea_surface_temp_c=record.sea_surface_temp_c,
        pfz_zone_active=record.pfz_zone_active,
        incois_warning_type=record.incois_warning_type,
        incois_alert_level=record.incois_alert_level
    )

    return ScenarioDefinition(
        scenario_code=record.scenario_code,
        role=record.role,
        title=record.title,
        location=record.location,
        narrative=record.narrative,
        ocean_data=ocean_data,
        options=opts,
        recommended_action_id=record.recommended_action_id,
        consequences=cons
    )

@router.get("", response_model=List[ScenarioDefinition])
def list_scenarios(
    role: Optional[str] = Query(None, description="Filter scenarios by role (fisherman, ship_captain, tourism_operator)"),
    db: Session = Depends(get_db)
):
    query = db.query(ScenarioRecord).filter(ScenarioRecord.is_active == True)
    if role:
        query = query.filter(ScenarioRecord.role == role.strip().lower())
    records = query.all()
    return [_to_scenario_definition(r) for r in records]

@router.get("/{scenario_code}", response_model=ScenarioDefinition)
def get_scenario(scenario_code: str, db: Session = Depends(get_db)):
    record = db.query(ScenarioRecord).filter(
        ScenarioRecord.scenario_code == scenario_code,
        ScenarioRecord.is_active == True
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_code}' not found")
    return _to_scenario_definition(record)

@router.get("/telemetry/stations", response_model=List[INCOISStation])
def get_incois_stations():
    provider = get_ocean_provider()
    return provider.list_stations()

@router.get("/telemetry/station/{station_id}", response_model=INCOISTelemetrySnapshot)
def get_station_telemetry(station_id: str):
    provider = get_ocean_provider()
    return provider.get_latest_telemetry(station_id)
