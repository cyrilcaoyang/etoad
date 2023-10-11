from logging import Logger
from Tests.test_utils import mk_logger_gui_free

"""
This script runs designated scripts in the current directory.
"""

script_list = [
    # "sampler_drain_dilute_discard.py",
    # "sampler_wash_refill.py",
    # "sampler_drain_dilute_discard.py",
    # "echem_CV_const_scan_rate.py",
    # # "sampler_liquid_addition.py",
    "echem_CV_const_scan_rate.py",
    "sampler_liquid_addition.py",
    "echem_CV_const_scan_rate.py",
    "sampler_liquid_addition.py",
    "echem_CV_const_scan_rate.py",
    "echem_CV_const_scan_rate.py",
    "sampler_liquid_addition.py",
    "echem_CV_const_scan_rate.py",
    "sampler_liquid_addition.py",
    "echem_CV_const_scan_rate.py",
    "sampler_liquid_addition.py",
    "echem_CV_const_scan_rate.py",
    "sampler_liquid_addition.py",
    "echem_CV_const_scan_rate.py",
    "sampler_liquid_addition.py",
    "echem_CV_const_scan_rate.py",
    "sampler_wash_refill.py"
]

logger = mk_logger_gui_free(
    sample_name=f"test_workflow",
    task_name=f"test_workflow",
)

for script in script_list:
    logger. debug(f"Running {script}...")
    try:
        exec(open(script).read())
        print(f"{script} executed successfully.")
    except Exception as e:
        print(f"Error running {script}: {e}")

print("All scripts executed.")

