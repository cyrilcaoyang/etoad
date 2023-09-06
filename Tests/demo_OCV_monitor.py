from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects
import time

"""
    This python script monitors Open Circuit Voltage over time, without using the Workflow Manager
"""

# ========== Sample Settings Below ========== #

SAMPLE_NAME = "K4[Fe(CN)6]-OCV"
TASK_NAME = "OCV_monitor"

Voltage_Interval = 0.01          # Unit: Voltage Interval in V
Time_Interval = 0.05               # Unit: Time Interval in s
Duration = 10                     # Unit: Duration in s

SIMULATION: bool = False          # This option can turn ON/OFF the Simulation Mode
DISABLE_GUI: bool = False         # This option can turn ON/OFF the GUI

# ========== Sample Settings Above ========== #


def do_measurement(simulation: bool, duration: float, logger: GraphicalInterface) -> None:

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation)
    start_time = time.time()

    while time.time() - start_time < Duration:
        results = potentiostat.do_measurement(
            technique="OCV",
            set_parameters={
                "IterationSettings": {
                    "no_iterations": 1
                },
                "TechniqueParameters": {
                    "Rest Time": {"value": Duration},
                    "Voltage Interval Size": {"value": Voltage_Interval},
                    "Time Interval Size": {"value": Time_Interval}
                }
            }
        )
    potentiostat.disconnect()

    csv_result = MakeObjects.mk_csv(results, logger=logger)

    # TODO: write a data analyzer for OCV
    # analyzer = MakeObjects.mk_analyzer(logger=logger)
    # analyzer.analyze_data(
    #     sample_name=logger.sample_name,
    #     experiment_name=logger.experiment_name,
    #     technique="OCV",
    #     analysis_settings={
    #         "Plot": {"title": f"OCV for {Duration} seconds"},
    #     },
    #     raw_data=results
    # )
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(TASK_NAME, SAMPLE_NAME, DISABLE_GUI)
    gui_logger.info(f"Starting {TASK_NAME} of {SAMPLE_NAME}.")

    worker_thread = ThreadWithReturn(target=do_measurement, args=(SIMULATION, Duration, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
