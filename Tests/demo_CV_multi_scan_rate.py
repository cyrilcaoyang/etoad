import test_utils.MakeObjects as MakeObjects
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn

"""
    This python script demonstrate the CV scans with multiple different scan rates.
    Without the usage of the GUI, the experiment can be run in the background.
    The results are analyzed and plotted.
"""

# ========== Sample Settings Below ========== #

SAMPLE_NAME = "K4[Fe(CN)6]"
TASK_NAME = "Constant Scan Rate CV"
V_init = 0                  # Unit: Initial Voltage in V
V_max = 0.5                 # Unit: Highest Voltage in V
V_min = 0                   # Unit: Lowest Voltage in V
V_fin = 0                   # Unit: Final Voltage in V

SCAN_RATES = [0.050, 0.100, 0.200, 0.400, 1.000]    # Unit: Scan Rate in V/s
CYCLE_NUM: int = 3      # The Numer of Cycles at each Scan Rate

DISABLE_GUI: bool = False
SIMULATION: bool = False    # This option can turn ON/OFF the Simulation Mode

# ========== Sample Settings Above ========== #


def do_measurement(scan_rates: list, simulation_mode: bool, logger: GraphicalInterface):

    num_iter = len(scan_rates)
    list_scan_rates = [[scan_rates[i] for _ in range(5)] for i in range(num_iter)]

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=False)
    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {"no_iterations": num_iter},
            "TechniqueParameters": {
                "Voltage Profile": {"value": [V_init, V_max, V_min, V_init, V_fin]},
                "Scan Rate": {
                    "changed_over_iterations": True,
                    "value": list_scan_rates
                },
                "Number of Cycles": {"value": CYCLE_NUM}
            }
        }
    )
    potentiostat.disconnect()

    MakeObjects.mk_csv(results, logger=logger)  # Saves Raw Data as a CVS file.

    analyzer = MakeObjects.mk_analyzer(logger=logger)
    analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="CV",
        analysis_settings={
            "Plot": {"title": "Cyclic Voltammetry of Multiple Scans"},
            "Peak Picking": {},
            "Integration": {}
        },
        raw_data=results
    )
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(TASK_NAME, SAMPLE_NAME, DISABLE_GUI)
    gui_logger.info(f"Starting {TASK_NAME} of {SAMPLE_NAME}.")

    worker_thread = ThreadWithReturn(target=do_measurement, args=(SCAN_RATES, SIMULATION, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
