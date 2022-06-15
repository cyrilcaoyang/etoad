from pathlib import Path
from SamplingSystem import SamplingSystem

SAMPLER_SETTINGS = Path(__file__).parent / "Settings" / "sampler_settings.json"

sampler = SamplingSystem(SAMPLER_SETTINGS, initial_wash=0)

sampler.dilute_cell(volume=0.2)
