from pathlib import Path
from SamplingSystem import SamplingSystem

SAMPLER_SETTINGS = Path(__file__).parent / "sampler_settings.json"

sampler = SamplingSystem(SAMPLER_SETTINGS)

sampler.transfer_to_cell(6, 2.0)

sampler.wash_cell(1.0)
