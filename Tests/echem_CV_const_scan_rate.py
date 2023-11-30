from typing import Any
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn, Timestamps

import Tests.utils_makeobjects as MakeObjects
from Tests.utils_unitoperations import do_experiment, do_analysis

"""
    This script demonstrate the CV scans with constant scan rates, with sample already in the Cell.
    The results are analyzed and plotted, and saved in the sample folder.
"""

# ========== Sample Settings Below ========== #

sample_name = f"FcCH2OH-Test_{Timestamps.timestamp_date()}"
# sample_name = f"K4[Fe(CN)6]_{Timestamps.timestamp_date()}"
task_name = "CV_Const_ScanRate_smooth-GC_Ag-AgCl"       # Specific test conditions.

channel_num: int = 2        # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True     # GUI can be disabled for simple liquid transfer.

V_init = 0.0     # Initial Voltage in V
V_max = 0.6     # Highest Voltage in V
V_min = 0.0       # Lowest Voltage in V
V_fin = 0.0     # Final Voltage in V
scan_rate = 0.100       # Scan Rate in V/s
cycle_num: int = 100              # The Numer of Cycles as an Integer, > 1

cv_test_settings: dict = {
    "IterationSett ings": {"no_iterations": 1},
    "TechniqueParameters": {
        "Voltage Profile": {"value": [V_init, V_max, V_min, V_init, V_fin]},
        "Scan Rate": {"value": [scan_rate] * 5},
        "Number of Cycles": {"value": cycle_num}
    }
}

cv_analysis_settings: dict = {
    "Plot": {"title": f"Cyclic Voltammetry at {scan_rate} V/s"},  # Plot Title
    "Peak Picking": {},  # Peak Picking for CV
    # "Integration": {},  # Integration for CV over iterations (1 in this case)
}

# ========== Sample Settings Above ========== #


def do_experiment_analysis(
        logger: GraphicalInterface,
        technique: str,
        channel: int,
        measurement_settings: dict,
        analysis_settings: dict,
) -> Any:

    exp_results = do_experiment(logger, technique, channel, measurement_settings)
    analysis_results = do_analysis(logger, technique, analysis_settings, exp_results)
    logger.stop_gui()
    return analysis_results


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(task_name, sample_name, enable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    worker_thread = ThreadWithReturn(
        target=do_experiment_analysis,
        args=(gui_logger, "CV", channel_num, cv_test_settings, cv_analysis_settings)
    )
    worker_thread.start()
    gui_logger.start_gui()
    result = worker_thread.join()

