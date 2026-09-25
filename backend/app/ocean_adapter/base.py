from abc import ABC, abstractmethod
from typing import List, Optional
from backend.app.ocean_adapter.models import (
    INCOISTelemetrySnapshot,
    OceanStateForecast,
    HighWaveAlert,
    PFZAdvisory,
    INCOISStation
)

class OceanDataProvider(ABC):
    """Abstract interface for Ocean Data Feeds.

    Identical method signatures whether data is generated from simulated fixtures
    or pulled from real live INCOIS REST APIs / Web Map Services.
    """

    @abstractmethod
    def get_latest_telemetry(self, station_id: str) -> INCOISTelemetrySnapshot:
        """Fetch real-time / current simulated ocean parameters for an INCOIS monitoring station."""
        pass

    @abstractmethod
    def get_active_warnings(self, zone: Optional[str] = None) -> List[HighWaveAlert]:
        """Fetch all active high wave, swell surge, or cyclone warnings."""
        pass

    @abstractmethod
    def get_pfz_advisories(self, landing_center: Optional[str] = None) -> List[PFZAdvisory]:
        """Fetch active Potential Fishing Zone coordinates and depth advisories."""
        pass

    @abstractmethod
    def list_stations(self) -> List[INCOISStation]:
        """List all coastal ocean stations monitored by the adapter."""
        pass
