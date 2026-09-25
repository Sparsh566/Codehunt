import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class INCOISStation(BaseModel):
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    zone: str  # Arabian Sea, Bay of Bengal, Indian Ocean, Andaman Sea

class OceanStateForecast(BaseModel):
    station: INCOISStation
    forecast_time: str
    significant_wave_height_m: float
    swell_wave_height_m: float
    swell_period_sec: float
    wind_speed_knots: float
    wind_direction_deg: float
    sea_surface_temp_c: float
    current_speed_m_per_s: float
    water_salinity_psu: float
    sea_state_code: int
    sea_state_desc: str

class HighWaveAlert(BaseModel):
    alert_id: str
    issue_date: str
    severity: str  # GREEN, YELLOW, ORANGE, RED
    warning_type: str  # High Wave Alert, Swell Surge Alert, Rough Sea Alert
    affected_coastline: str
    max_wave_height_m: float
    period_hours: int
    advisory_text: str

class PFZAdvisory(BaseModel):
    advisory_id: str
    landing_center: str
    bearing_degrees: float
    distance_km: float
    depth_m: int
    sst_gradient: float
    chlorophyll_a: float
    valid_until: str
    species_expected: List[str]

class INCOISTelemetrySnapshot(BaseModel):
    provider: str = "INCOIS-Simulated-Adapter-v2"
    timestamp: str
    station: INCOISStation
    forecast: OceanStateForecast
    active_warning: Optional[HighWaveAlert] = None
    pfz_advisory: Optional[PFZAdvisory] = None
