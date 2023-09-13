import time, pprint
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script measures Open Circuit Voltage (OCV) over time, until the voltage is stable.
    The experiment will be run in cycles of multiple steps of OCV measurements.
    The cycles will only stop when the ALL the steps of OCV measurements are stable.
    Or, the cycles will stop after max_cycles.
    
    The Data directory is defined by .test_utils.PathFinder.py that read settings from .test_settings.data_settings.
    The result will be saved in the Data / "Data" Directory.
    The logs will be saved in the Data / "Log" Directory.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]-OCV-Until-Stable2"   # Sample Name will the name of the folder that contains the data
task_name = "Stable_Open_Circuit_Voltage"

voltage_interval = 0.1            # Unit: Voltage Interval in mV
time_interval = 0.05              # Unit: Time Interval in s
time_per_step = 15                # Unit: Time per Step in s
steps = 4                         # Unit: Number of Steps per cycle
max_cycles = 30                   # Unit: Maximum Number of Cycles of Steps

enable_gui: bool = False           # This option can turn ON/OFF the GUI

# ========== Sample Settings Above ========== #


def do_measurement(simulation: bool, logger: GraphicalInterface) -> dict:

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation)
    start_time = time.time()

    while time.time() - start_time < time_per_step:
        results = potentiostat.do_measurement(
            technique="OCV",
            set_parameters={
                "IterationSettings": {
                    "no_iterations": steps
                },
                "TechniqueParameters": {
                    "Voltage Interval Size": {"value": voltage_interval},
                    "Time Interval Size": {"value": time_interval},
                    "Rest Time": {"value": time_per_step}
                }
            }
        )

    analyzer = MakeObjects.mk_analyzer(logger=logger)
    analysis_results = analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="OCV",
        analysis_settings={
            "Plot": {"title": f"OCV for {time_per_step} seconds"},
            "Voltage": {}
        },
        raw_data=results,
    )
    gui_logger.stop_gui()
    return analysis_results


if __name__ == "__main__":

    simulation = False
    job_logger = MakeObjects.mk_logger_gui_free(task_name, sample_name)
    job_logger.info(f"Starting {task_name} of {sample_name}.")

    for x in range(max_cycles):
        gui_logger = MakeObjects.mk_logger(task_name+f"_attempt_{x}", sample_name, enable_gui)
        gui_logger.info(f"Starting {task_name} of {sample_name}, attempt {x}.")

        # The worker thread will run the measurement, and return the result to cycle_result.
        worker_thread = ThreadWithReturn(target=do_measurement, args=(simulation, gui_logger))
        worker_thread.start()
        gui_logger.start_gui()
        cycle_result = worker_thread.join()

        # The measurement will only stop when all the measurements in cycle_result are stable.
        V_first = float(cycle_result[f"Iteration {0}"]["Voltage Average"])
        V_fin = float(cycle_result[f"Iteration {steps - 1}"]["Voltage Average"])
        V_std = float(cycle_result[f"Iteration {steps - 1}"]["Voltage Std Deviation"])
        if (all(cycle_result[f"Iteration {i}"]["Is Voltage Stable"] for i in range(steps))
                and (abs(V_first - V_fin) <= V_std/2)):
            job_logger.info(f"The voltage has stabled after {x+1} cycles to {V_fin} volts. Experiment Completed.")
            break
        else:
            job_logger.info(f"The voltage has not stabled after {x + 1} cycles. Continuing experiment."
                            f"Analysis result for {x + 1} cycle: {pprint.pformat(cycle_result)}")
            continue
    else:
        # This else statement is executed when the for loop is not terminated by a break statement.
        job_logger.info(f"The voltage has not stabled after {max_cycles} cycles. Experiment Completed.")





