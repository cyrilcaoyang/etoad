import time
from pathlib import Path
from SamplingSystem import SamplingSystem
from SamplingSystem.AtmosphereHandler import AtmosphereHandler
from Utils import ConfigLoader

SAMPLER_SETTINGS = Path(__file__).parent / "Settings" / "sampler_settings.json"

# sampler = SamplingSystem(SAMPLER_SETTINGS, initial_wash=0)
# sampler.dilute_cell(volume=0.2)

relay_settings: dict = ConfigLoader.load_config(SAMPLER_SETTINGS)["relay_settings"]

atm_controller: AtmosphereHandler = AtmosphereHandler(**relay_settings)

with atm_controller.open_atmosphere():
    time.sleep(5)