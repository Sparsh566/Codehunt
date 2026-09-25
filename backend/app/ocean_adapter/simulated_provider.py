import datetime
import math
from typing import List, Optional, Dict
from backend.app.ocean_adapter.base import OceanDataProvider
from backend.app.ocean_adapter.models import (
    INCOISStation,
    OceanStateForecast,
    HighWaveAlert,
    PFZAdvisory,
    INCOISTelemetrySnapshot
)

STATIONS: Dict[str, INCOISStation] = {
    "STN-VERAVAL": INCOISStation(
        station_id="STN-VERAVAL",
        station_name="Veraval Offshore Buoy",
        latitude=20.90,
        longitude=70.36,
        zone="Arabian Sea"
    ),
    "STN-RATNAGIRI": INCOISStation(
        station_id="STN-RATNAGIRI",
        station_name="Ratnagiri Coastal Observatory",
        latitude=16.99,
        longitude=73.30,
        zone="Arabian Sea"
    ),
    "STN-PARADIP": INCOISStation(
        station_id="STN-PARADIP",
        station_name="Paradip Deepwater Anchor",
        latitude=20.26,
        longitude=86.67,
        zone="Bay of Bengal"
    ),
    "STN-KOVALAM": INCOISStation(
        station_id="STN-KOVALAM",
        station_name="Kovalam Headland Station",
        latitude=8.40,
        longitude=76.97,
        zone="Indian Ocean"
    ),
    "STN-LAKSHADWEEP": INCOISStation(
        station_id="STN-LAKSHADWEEP",
        station_name="Kavaratti Reef Platform",
        latitude=10.56,
        longitude=72.64,
        zone="Arabian Sea"
    )
}

class SimulatedINCOISProvider(OceanDataProvider):
    """Simulated INCOIS Ocean Data Provider.

    Replicates the exact payload schemas, telemetry intervals, and alert formats
    emitted by INCOIS's Ocean State Forecast (OSF) and Advisory Web Services.
    """

    def __init__(self):
        self.stations = STATIONS

    def list_stations(self) -> List[INCOISStation]:
        return list(self.stations.values())

    def get_latest_telemetry(self, station_id: str) -> INCOISTelemetrySnapshot:
        station = self.stations.get(station_id, self.stations["STN-VERAVAL"])
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Deterministic simulation seeded by station
        if station_id == "STN-VERAVAL":
            forecast = OceanStateForecast(
                station=station,
                forecast_time=now_iso,
                significant_wave_height_m=3.8,
                swell_wave_height_m=2.9,
                swell_period_sec=14.2,
                wind_speed_knots=34.0,
                wind_direction_deg=240.0,
                sea_surface_temp_c=28.4,
                current_speed_m_per_s=1.2,
                water_salinity_psu=35.8,
                sea_state_code=4,
                sea_state_desc="Rough"
            )
            warning = HighWaveAlert(
                alert_id="HWA-ARA-2026-081",
                issue_date=now_iso,
                severity="ORANGE",
                warning_type="High Wave Alert",
                affected_coastline="Saurashtra to South Gujarat",
                max_wave_height_m=4.2,
                period_hours=36,
                advisory_text="High waves in the range of 3.5 to 4.2 meters are forecasted. Fishermen are advised not to venture into deep sea."
            )
            pfz = PFZAdvisory(
                advisory_id="PFZ-GUJ-881",
                landing_center="Veraval",
                bearing_degrees=215.0,
                distance_km=32.0,
                depth_m=45,
                sst_gradient=0.8,
                chlorophyll_a=1.4,
                valid_until=now_iso,
                species_expected=["Sardinella", "Indian Mackerel", "Ribbonfish"]
            )
        elif station_id == "STN-PARADIP":
            forecast = OceanStateForecast(
                station=station,
                forecast_time=now_iso,
                significant_wave_height_m=5.4,
                swell_wave_height_m=4.6,
                swell_period_sec=16.0,
                wind_speed_knots=52.0,
                wind_direction_deg=110.0,
                sea_surface_temp_c=29.6,
                current_speed_m_per_s=2.4,
                water_salinity_psu=31.2,
                sea_state_code=5,
                sea_state_desc="Very Rough to High"
            )
            warning = HighWaveAlert(
                alert_id="CYC-BOB-2026-004",
                issue_date=now_iso,
                severity="RED",
                warning_type="Severe Cyclonic Storm Warning",
                affected_coastline="North Odisha to West Bengal Coast",
                max_wave_height_m=6.5,
                period_hours=48,
                advisory_text="Extremely rough to high seas expected. Total suspension of all merchant shipping and fishing operations."
            )
            pfz = None
        elif station_id == "STN-KOVALAM":
            forecast = OceanStateForecast(
                station=station,
                forecast_time=now_iso,
                significant_wave_height_m=2.2,
                swell_wave_height_m=1.8,
                swell_period_sec=15.0,
                wind_speed_knots=18.0,
                wind_direction_deg=210.0,
                sea_surface_temp_c=28.1,
                current_speed_m_per_s=0.9,
                water_salinity_psu=34.5,
                sea_state_code=3,
                sea_state_desc="Moderate"
            )
            warning = HighWaveAlert(
                alert_id="RIP-IND-2026-019",
                issue_date=now_iso,
                severity="YELLOW",
                warning_type="Rip Current & Swell Surge Alert",
                affected_coastline="South Kerala Coast (Vizhinjam to Kovalam)",
                max_wave_height_m=2.6,
                period_hours=24,
                advisory_text="Strong rip currents and swell surges along shallow beaches. Lifeguards and tourism boats must restrict water activities."
            )
            pfz = None
        else:
            # Default calm / normal station
            forecast = OceanStateForecast(
                station=station,
                forecast_time=now_iso,
                significant_wave_height_m=1.2,
                swell_wave_height_m=0.9,
                swell_period_sec=9.5,
                wind_speed_knots=12.0,
                wind_direction_deg=180.0,
                sea_surface_temp_c=27.9,
                current_speed_m_per_s=0.5,
                water_salinity_psu=35.0,
                sea_state_code=2,
                sea_state_desc="Smooth to Slight"
            )
            warning = None
            pfz = PFZAdvisory(
                advisory_id=f"PFZ-GEN-{station_id[-3:]}",
                landing_center=station.station_name,
                bearing_degrees=190.0,
                distance_km=18.0,
                depth_m=35,
                sst_gradient=0.6,
                chlorophyll_a=1.1,
                valid_until=now_iso,
                species_expected=["Tuna", "Mackerel"]
            )

        return INCOISTelemetrySnapshot(
            provider="INCOIS-Simulated-Adapter-v2",
            timestamp=now_iso,
            station=station,
            forecast=forecast,
            active_warning=warning,
            pfz_advisory=pfz
        )

    def get_active_warnings(self, zone: Optional[str] = None) -> List[HighWaveAlert]:
        alerts = []
        for stn_id in self.stations:
            snapshot = self.get_latest_telemetry(stn_id)
            if snapshot.active_warning:
                if not zone or snapshot.station.zone == zone:
                    alerts.append(snapshot.active_warning)
        return alerts

    def get_pfz_advisories(self, landing_center: Optional[str] = None) -> List[PFZAdvisory]:
        pfzs = []
        for stn_id in self.stations:
            snapshot = self.get_latest_telemetry(stn_id)
            if snapshot.pfz_advisory:
                if not landing_center or landing_center.lower() in snapshot.pfz_advisory.landing_center.lower():
                    pfzs.append(snapshot.pfz_advisory)
        return pfzs
