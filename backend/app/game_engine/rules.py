"""Maritime safety rules, Beaufort scale conversions, and INCOIS advisory thresholds.

All functions in this module are PURE, DETERMINISTIC, and contain ZERO AI dependencies.
"""

from typing import Dict, Any

# INCOIS Alert Thresholds
WAVE_HEIGHT_YELLOW_ALERT = 2.5  # meters
WAVE_HEIGHT_ORANGE_ALERT = 3.5  # meters
WAVE_HEIGHT_RED_WARNING = 4.5   # meters

WIND_SPEED_MODERATE_KTS = 20.0  # knots
WIND_SPEED_STRONG_KTS = 28.0    # knots
WIND_SPEED_GALE_KTS = 34.0      # knots (Near Gale / Gale)
WIND_SPEED_STORM_KTS = 48.0     # knots (Storm / Cyclone)

def classify_sea_state(wave_height_m: float) -> Dict[str, Any]:
    """WMO Sea State Code classification based on significant wave height."""
    if wave_height_m < 0.1:
        return {"code": 0, "description": "Calm (glassy)", "danger_level": "none"}
    elif wave_height_m < 0.5:
        return {"code": 1, "description": "Calm (rippled)", "danger_level": "none"}
    elif wave_height_m < 1.25:
        return {"code": 2, "description": "Smooth", "danger_level": "low"}
    elif wave_height_m < 2.5:
        return {"code": 3, "description": "Slight to Moderate", "danger_level": "caution"}
    elif wave_height_m < 4.0:
        return {"code": 4, "description": "Rough", "danger_level": "high"}
    elif wave_height_m < 6.0:
        return {"code": 5, "description": "Very Rough", "danger_level": "severe"}
    else:
        return {"code": 6, "description": "High / Phenomenal", "danger_level": "extreme"}

def classify_wind_beaufort(wind_speed_knots: float) -> Dict[str, Any]:
    """Beaufort scale classification from sustained wind speeds in knots."""
    if wind_speed_knots < 1:
        return {"force": 0, "name": "Calm"}
    elif wind_speed_knots <= 3:
        return {"force": 1, "name": "Light air"}
    elif wind_speed_knots <= 6:
        return {"force": 2, "name": "Light breeze"}
    elif wind_speed_knots <= 10:
        return {"force": 3, "name": "Gentle breeze"}
    elif wind_speed_knots <= 16:
        return {"force": 4, "name": "Moderate breeze"}
    elif wind_speed_knots <= 21:
        return {"force": 5, "name": "Fresh breeze"}
    elif wind_speed_knots <= 27:
        return {"force": 6, "name": "Strong breeze"}
    elif wind_speed_knots <= 33:
        return {"force": 7, "name": "Near gale"}
    elif wind_speed_knots <= 40:
        return {"force": 8, "name": "Gale"}
    elif wind_speed_knots <= 47:
        return {"force": 9, "name": "Strong gale"}
    elif wind_speed_knots <= 55:
        return {"force": 10, "name": "Storm"}
    else:
        return {"force": 11, "name": "Violent storm / Cyclone"}

def check_role_safety_thresholds(
    role: str,
    wave_height_m: float,
    wind_speed_knots: float,
    incois_alert_level: str
) -> Dict[str, Any]:
    """Determines whether environmental conditions violate operational limits for a role."""
    role = role.lower()
    
    if role == "fisherman":
        # Small artisanal and mechanized fishing craft (< 20m length)
        max_safe_wave = 2.5
        max_safe_wind = 25.0
        allowed_alerts = ["GREEN", "YELLOW"]
    elif role == "pirate_king":
        # Pirate galleon/schooner: agile sea voyager, respects shallow reef limits and swell surges
        max_safe_wave = 2.8
        max_safe_wind = 28.0
        allowed_alerts = ["GREEN", "YELLOW"]
    elif role == "ship_captain":
        # Larger merchant/cargo vessels
        max_safe_wave = 4.5
        max_safe_wind = 40.0
        allowed_alerts = ["GREEN", "YELLOW", "ORANGE"]
    else:
        max_safe_wave = 2.5
        max_safe_wind = 25.0
        allowed_alerts = ["GREEN"]

    exceeds_wave = wave_height_m > max_safe_wave
    exceeds_wind = wind_speed_knots > max_safe_wind
    alert_violates = incois_alert_level.upper() not in allowed_alerts

    is_inherently_hazardous = exceeds_wave or exceeds_wind or alert_violates

    return {
        "is_inherently_hazardous": is_inherently_hazardous,
        "max_safe_wave": max_safe_wave,
        "max_safe_wind": max_safe_wind,
        "wave_exceeded": exceeds_wave,
        "wind_exceeded": exceeds_wind,
        "alert_violates": alert_violates,
    }
