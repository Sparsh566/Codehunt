from backend.app.config import settings
from backend.app.ocean_adapter.base import OceanDataProvider
from backend.app.ocean_adapter.simulated_provider import SimulatedINCOISProvider

_provider_instance: OceanDataProvider = None

def get_ocean_provider() -> OceanDataProvider:
    """Singleton getter for the configured OceanDataProvider."""
    global _provider_instance
    if _provider_instance is None:
        if settings.OCEAN_DATA_PROVIDER == "simulated":
            _provider_instance = SimulatedINCOISProvider()
        else:
            # Drop-in point for LiveINCOISProvider
            _provider_instance = SimulatedINCOISProvider()
    return _provider_instance

__all__ = ["OceanDataProvider", "SimulatedINCOISProvider", "get_ocean_provider"]
