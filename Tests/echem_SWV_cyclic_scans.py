from typing import Any
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn, Timestamps

import Tests.utils_makeobjects as MakeObjects
from Tests.utils_unitoperations import do_experiment, do_analysis, cyclic_swv_voltage_parser

"""
    This python script demonstrate cyclic SWV scans, with sample already in the Cell.
    The results are analyzed and plotted, and saved in the sample folder.
"""

# ========== Sample Settings Below ========== #

sample_name = f"SampleName_{Timestamps.timestamp_date()}"
# sample_name = f"K4[Fe(CN)6]_{Timestamps.timestamp_date()}"
task_name = "SWV_cyclic_scans_smooth-GC_Pt_SHE"

V_init = 1.0                                                  # Initial Voltage in V
V_fin = -0.2                                                  # Final Voltage in V
T_rest = 10                                                    # The Resting Time Before the Scan in seconds
cycle_num = 1

channel_num: int = 2                                           # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True                                         # This option can turn ON/OFF the GUI
simulation: bool = False                                        # This option can turn ON/OFF the simulation mode

Pulse_h = 0.025                                                 # Pulse Height in V, default: 0.025
Pulse_w = 0.200                                                 # Pulse Width in seconds, default: 0.200
Step_h = 0.010                                                  # Step Height in V, default: 0.010
average_percent = 0.800                                         # Averaging Percent Interval (0,1), default: 0.800

# ========== Sample Settings Above ========== #

list_v_init, list_v_fin = cyclic_swv_voltage_parser(V_init, V_fin, cycle_num)

swv_test_settings: dict = {
    "IterationSettings": {"no_iterations": 2 * cycle_num},
    "TechniqueParameters": {
        "Initial Voltage": {
            "changed_over_iterations": True,
            "value": list_v_init
        },
        "Final Voltage":  {
            "changed_over_iterations": True,
            "value": list_v_fin
        },
        "Rest Time": {"value": T_rest},
        "Pulse Height": {"value": Pulse_h},
        "Pulse Width": {"value": Pulse_w},
        "Step Height": {"value": Step_h},
        "Start Averaging Interval": {"value": average_percent},
        "End Averaging Interval": {"value": 1.0}
    }
}

swv_analysis_settings: dict = {
    "Plot": {"title": "A Single Scan of SWV"},
    "Peak Picking": {},
    # "Integration": {}
}


def do_experiment_analysis(
        logger: GraphicalInterface,
        technique: str,
        channel: int,
        measurement_settings: dict,
        analysis_settings: dict,
) -> Any:

    logger.info(f"The list of initial voltages is: {list_v_init}")
    logger.info(f"The list of final voltages is: {list_v_fin}")
    exp_results = do_experiment(logger, technique, channel, measurement_settings)
    analysis_results = do_analysis(logger, technique, analysis_settings, exp_results)
    logger.stop_gui()
    return analysis_results


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(task_name, sample_name, enable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    worker_thread = ThreadWithReturn(
        target=do_experiment_analysis,
        args=(gui_logger, "SWV", channel_num, swv_test_settings, swv_analysis_settings)
    )
    worker_thread.start()
    gui_logger.start_gui()
    result = worker_thread.join()
