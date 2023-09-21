import test_utils.MakeObjects as MakeObjects
from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn

"""
    This python script demonstrate the CV scans with multiple different scan rates, without using the Workflow Manager.
    Without the usage of the GUI, the experiment can be run in the background.
    The results are analyzed and plotted.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]_CV-Multi-ScanRate"
task_name = "CV_Const_ScanRate_smooth-GC_Pt_SHE"
V_init = 0.4                                                    # Initial Voltage in V
V_max = 1.2                                                     # Highest Voltage in V
V_min = 0.4                                                     # Lowest Voltage in V
V_fin = 0.4                                                     # Final Voltage in V

scan_rates = [0.025, 0.050, 0.100, 0.200, 0.500]                # Unit: Scan Rate in V/s
cycle_num: int = 3                                              # The Numer of Cycles at each Scan Rate

channel_num: int = 2                                            # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True                                         # This option can turn ON/OFF the GUI
simulation: bool = False                                        # This option can turn ON/OFF the simulation mode

# ========== Sample Settings Above ========== #


def do_measurement(logger: GraphicalInterface, v_range: list, rates: list, channel: int, simulation_opt: bool):

    num_iter = len(rates)
    list_scan_rates = [[rates[i] for _ in range(5)] for i in range(num_iter)]

    potentiostat = MakeObjects.mk_potentiostat(logger=logger, channel= channel, sim=simulation_opt)
    results = potentiostat.do_measurement(
        technique="CV",
        set_parameters={
            "IterationSettings": {"no_iterations": num_iter},
            "TechniqueParameters": {
                "Voltage Profile": {"value": v_range},
                "Scan Rate": {
                    "changed_over_iterations": True,
                    "value": list_scan_rates
                },
                "Number of Cycles": {"value": cycle_num}
            },
        },
        channel=channel
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

    V_range = [V_init, V_max, V_min, V_init, V_fin]
    worker_thread = ThreadWithReturn(
        target=do_measurement,
        args=(gui_logger, V_range, scan_rates, channel_num, simulation)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
