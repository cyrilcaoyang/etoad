from typing import Any
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn, Timestamps

import Tests.utils_makeobjects as MakeObjects
from Tests.utils_unitoperations import do_experiment, do_analysis

"""
    This python script demonstrate the CV scans with multiple different scan rates, with sample already in the Cell.
    The results are analyzed and plotted, and saved in the sample folder.
"""

# ========== Sample Settings Below ========== #

sample_name = f"Sample_10M_var_rate_{Timestamps.timestamp_date()}"       # The name of the folder that contains the data.
task_name = "CV_Const_ScanRate_smooth-GC_Ag-AgCl"       # Specific test conditions.

channel_num: int = 2        # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True     # GUI can be disabled for simple liquid transfer.

V_init = -0.5      # Initial Voltage in V
V_max = 0.8     # Highest Voltage in V
V_min = -0.5       # Lowest Voltage in V
V_fin = -0.5     # Final Voltage in V
scan_rates = [0.200, 0.225, 0.300, 0.400, 0.500, 0.625]
## scan_rates = [0.020, 0.025, 0.040, 0.050, 0.075, 0.100, 0.150, 0.200, 0.225, 0.300, 0.400, 0.500, 0.625]
cycle_num: int = 5      # The Numer of Cycles at each Scan Rate

cv_test_settings: dict = {
    "IterationSettings": {"no_iterations": len(scan_rates)},
    "TechniqueParameters": {
        "Voltage Profile": {"value": [V_init, V_max, V_min, V_init, V_fin]},
        "Scan Rate": {
        "changed_over_iterations": True,
        "value": [[scan_rates[i] for _ in range(5)] for i in range(len(scan_rates))]
        },
        "Number of Cycles": {"value": cycle_num}
    }
}

cv_analysis_settings: dict = {
    "Plot": {"title": f"Cyclic Voltammetry at Various Scan Rates"},  # Plot Title
    "Peak Picking": {},     # Peak Picking for CV
    "Integration": {},      # Integration for CV over iterations (1 in this case)
    "Peaks Scanrate": {},       #
    "Currents Scanrate": {},        #
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
