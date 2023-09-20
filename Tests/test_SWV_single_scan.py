from etoad.Interface.GraphicalInterface import GraphicalInterface
from etoad.Utils import ThreadWithReturn
from test_utils.MakeObjects import mk_analyzer, mk_logger
from test_utils.MeasurePlot import measure_swv

"""
    This python script demonstrate a simple SWV scan, without using the Workflow Manager.
    Without the usage of the GUI, the experiment can be run in the background.
    The results are analyzed and plotted.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]_Pulse_Voltammetry"
task_name = "SWV_single_scan_smooth-GC_Pt_SHE"

V_init = 1.2                                                    # Initial Voltage in V
V_fin = -0.5                                                    # Final Voltage in V
T_rest = 10                                                     # The Resting Time Before the Scan in seconds

channel_num: int = 2                                            # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True                                         # This option can turn ON/OFF the GUI
simulation: bool = False                                        # This option can turn ON/OFF the simulation mode

# ========== Pulse Settings Below ========== #

Pulse_h = 0.025                                                 # Pulse Height in V, default: 0.025
Pulse_w = 0.200                                                 # Pulse Width in seconds, default: 0.200
Step_h = 0.010                                                  # Step Height in V, default: 0.010
average_percent = 0.800                                         # Averaging Percent Interval (0,1), default: 0.800

# ========== Pulse Settings Above ========== #


def do_measurement(
    logger: GraphicalInterface,
    para_range_time: tuple,
    pulse_para: tuple,
    channel: int,
    simulation_opt: bool
) -> None:

    swv_result = measure_swv(logger, para_range_time, pulse_para, channel, simulation_opt)

    analyzer = mk_analyzer(logger=logger)
    analyzer.analyze_data(
        sample_name=logger.sample_name,
        experiment_name=logger.experiment_name,
        technique="SWV",
        analysis_settings={
            "Plot": {"title": "A Single Scan of SWV"},
            "Peak Picking": {},
            "Integration": {}
        },
        raw_data=swv_result
    )
    logger.stop_gui()


if __name__ == "__main__":

    gui_logger = mk_logger(task_name, sample_name, enable_gui)
    gui_logger.info(f"Starting {task_name} of {sample_name}.")

    range_time = (V_init, V_fin, T_rest)
    P_para = (Pulse_h, Pulse_w, Step_h, average_percent)
    worker_thread = ThreadWithReturn(
        target=do_measurement,
        args=(gui_logger, range_time, P_para, channel_num, simulation)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
