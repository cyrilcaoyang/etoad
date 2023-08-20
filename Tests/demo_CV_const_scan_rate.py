from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
import test_utils.MakeObjects as MakeObjects

"""
    This python script demonstrate the CV scans with constant scan rates, without using the Workflow Manager
    Without the usage of the GUI, the experiment can be run in the background.
"""

# ========== Sample Settings Below ========== #

SAMPLE_NAME = "K4[Fe(CN)6]"
TASK_NAME = "CV_Const_ScanRate"
V_init = 0                  # Unit: Initial Voltage in V
V_max = 0.5                 # Unit: Highest Voltage in V
V_min = 0                   # Unit: Lowest Voltage in V
V_fin = 0                   # Unit: Final Voltage in V
SCAN_RATE = 0.100           # Unit: Scan Rate in V/s
CYCLE_NUM: int = 10     # The Numer of Cycles as an Integer

DISABLE_GUI: bool = False
SIMULATION: bool = False    # This option can turn ON/OFF the Simulation Mode

# ========== Sample Settings Above ========== #


def do_measurement(simulation: bool, logger: GraphicalInterface) -> None:

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation)
    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {
                "no_iterations": 1
            },
            "TechniqueParameters": {
                "Voltage Profile": {
                    "value": [V_init, V_max, V_min, V_init, V_fin]
                },
                "Scan Rate": {"value": [SCAN_RATE]*5},
                "Number of Cycles": {"value": CYCLE_NUM}
            }
        }
    )

    MakeObjects.mk_csv(results, logger=logger)  # Saves Raw Data as CVS file
    potentiostat.disconnect()
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(TASK_NAME, SAMPLE_NAME, DISABLE_GUI)
    gui_logger.info(f"Starting {TASK_NAME} of {SAMPLE_NAME}.")

    worker_thread = ThreadWithReturn(target=do_measurement, args=(SIMULATION, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
