import test_utils.MakeObjects as MakeObjects
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn

"""
    This python script demonstrate the CV scans with multiple different scan rates, without using the Workflow Manager.
    Without the usage of the GUI, the experiment can be run in the background.
    The results are analyzed and plotted.
    
    The Data directory:
    is defined by .test_utils.PathFinder.py,
    which read settings read from .test_settings.data_settings.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]_CV_scan_rate"
task_name = "Multiple_Rate_0.2mM_cell"
V_init = -0.2               # Unit: Initial Voltage in V
V_max = 0.8                 # Unit: Highest Voltage in V
V_min = -0.2                # Unit: Lowest Voltage in V
V_fin = 0                   # Unit: Final Voltage in V

scan_rates = [0.025, 0.050, 0.100, 0.200, 0.500]    # Unit: Scan Rate in V/s
cycle_num: int = 5          # The Numer of Cycles at each Scan Rate

enable_gui: bool = False    # This option can turn ON/OFF the GUI

# ========== Sample Settings Above ========== #


def do_measurement(scan_rates: list, simulation_mode: bool, logger: GraphicalInterface):

    num_iter = len(scan_rates)
    list_scan_rates = [[scan_rates[i] for _ in range(5)] for i in range(num_iter)]

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, simulation_mode=simulation_mode)
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
                "Number of Cycles": {"value": cycle_num}
            }
        }
    )
    potentiostat.disconnect()

    analyzer = MakeObjects.mk_analyzer(logger=logger)
    analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="CV",
        analysis_settings={
            "Plot": {"title": "Cyclic Voltammetry of Multiple Scans"},
            "Peak Picking": {},
            "Integration": {},
            "Peaks Scanrate": {},
            "Currents Scanrate": {}
        },
        raw_data=results
    )
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(task_name, sample_name, enable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    simulation = False
    worker_thread = ThreadWithReturn(target=do_measurement, args=(scan_rates, simulation, gui_logger))
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
