import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from backend.app.db.session import Base

class ScenarioRecord(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, index=True)
    scenario_code = Column(String(50), unique=True, index=True, nullable=False)
    role = Column(String(50), index=True, nullable=False)  # fisherman, ship_captain, tourism_operator
    title = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    narrative = Column(Text, nullable=False)
    
    # INCOIS Ocean Telemetry
    wave_height_m = Column(Float, nullable=False)
    wind_speed_knots = Column(Float, nullable=False)
    swell_period_sec = Column(Float, default=10.0)
    sea_surface_temp_c = Column(Float, default=28.0)
    pfz_zone_active = Column(Boolean, default=False)
    incois_warning_type = Column(String(100), default="none")  # none, high_wave, rough_sea, cyclone, tsunami
    incois_alert_level = Column(String(50), default="GREEN")    # GREEN, YELLOW, ORANGE, RED
    
    # Options & Evaluation Rules stored as JSON text
    options_json = Column(Text, nullable=False)
    recommended_action_id = Column(String(50), nullable=False)
    consequences_json = Column(Text, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
