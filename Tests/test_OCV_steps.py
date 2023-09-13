from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects
import time

"""
    This python script monitors Open Circuit Voltage (OCV) over time, in steps of time_per_step.
    
    The Data directory is defined by .test_utils.PathFinder.py that read settings from .test_settings.data_settings.
    The result will be saved in the Data / "Data" Directory.
    The logs will be saved in the Data / "Log" Directory.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]-OCV"   # Sample Name will the name of the folder that contains the data
task_name = "OCV_steps"

voltage_interval = 0.1            # Unit: Voltage Interval in mV
time_interval = 0.05              # Unit: Time Interval in s
time_per_step = 15                # Unit: Time per Step in s
steps = 1                         # Unit: Number of Steps per cycle

enable_gui: bool = True           # This option can turn ON/OFF the GUI

# ========== Sample Settings Above ========== #


def do_measurement(simulation: bool, logger: GraphicalInterface) -> None:

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
    analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="OCV",
        analysis_settings={
            "Plot": {"title": f"OCV for {time_per_step} seconds"},
            "Voltage": {}
        },
        raw_data=results,
    )
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(task_name, sample_name, enable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    simulation = False
    worker_thread = ThreadWithReturn(target=do_measurement, args=(simulation, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
