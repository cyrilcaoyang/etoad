import time
from logging import Logger
from utils_makeobjects import mk_logger_gui_free

"""
This script runs designated scripts in the current directory.
"""

script_list = [
    # "sampler_drain_dilute_discard.py",
    # "sampler_wash_refill.py",
    "sampler_drain_dilute_discard.py",
    "echem_CV_const_scan_rate.py",
    # "echem_CV_const_scan_rate.py",
    "sampler_wash_refill.py"
]

for _ in range(10):
    logger = mk_logger_gui_free(
        sample_name=f"test_workflow",
        task_name=f"test_workflow",
    )
    for script in script_list:
        logger. debug(f"Running {script}...")
        try:
            exec(open(script).read())
            print(f"{script} executed successfully.")
            time.sleep(5)
        except Exception as e:
            print(f"Error running {script}: {e}")

# print("All scripts executed.")

