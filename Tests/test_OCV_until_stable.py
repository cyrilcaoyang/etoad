import pprint
from etoad.Utils import ThreadWithReturn
from Tests.utils_makeobjects import mk_logger_gui_free, mk_logger
from Tests.utils_measureplot import measure_plot_ocv

"""
    This python script measures Open Circuit Voltage (OCV) over time, until the voltage is stable.
    The experiment will be run in cycles of multiple steps of OCV measurements.
    The cycles will only stop when the ALL the steps of OCV measurements are stable.
    Or, the cycles will stop after max_cycles.
"""

# ========== Sample Settings Below ========== #

sample_name = "K4[Fe(CN)6]-OCV-Until-Stable"   # Sample Name will the name of the folder that contains the data
task_name = "Stable_Open_Circuit_Voltage"

T_step = 15                       # Time per Step of Measurements in s, default: 15
voltage_interval = 0.1            # Unit: Voltage Interval in mV
time_interval = 0.05              # Unit: Time Interval Size in s
steps = 4                         # Unit: Number of Steps per cycle, all steps must be stable to end the cycle
max_cycles = 30                   # Unit: Maximum number of cycles

channel_num: int = 2              # The channel number of the potentiostat, either 1 or 2.
enable_gui: bool = True          # This option can turn ON/OFF the GUI
simulation: bool = False          # This option can turn ON/OFF the simulation mode

# ========== Sample Settings Above ========== #


if __name__ == "__main__":

    parameters = (T_step, voltage_interval, time_interval, steps)
    job_logger = mk_logger_gui_free(task_name, sample_name)     # This logger will not start the GUI.
    job_logger.info(f"Starting {task_name} of {sample_name}.")

    for x in range(max_cycles):
        gui_logger = mk_logger(task_name+f"_attempt_{x + 1}", sample_name, enable_gui)
        gui_logger.info(f"Starting {task_name} of {sample_name}, attempt {x + 1}.")

        # The worker thread will run the measurement, and return the result to cycle_result.
        worker_thread = ThreadWithReturn(
            target=measure_plot_ocv,
            args=(gui_logger, parameters, channel_num, simulation)
        )
        worker_thread.start()
        gui_logger.start_gui()
        cycle_result = worker_thread.join()

        # The measurement will only stop when all the measurements in cycle_result are stable.
        V_first = float(cycle_result[f"Iteration {0}"]["Voltage Average"])
        V_fin = float(cycle_result[f"Iteration {steps - 1}"]["Voltage Average"])
        V_std = float(cycle_result[f"Iteration {steps - 1}"]["Voltage Std Deviation"])
        if all(cycle_result[f"Iteration {i}"]["Is Voltage Stable"] for i in range(steps)):
            job_logger.info(f"The voltage has stabled after {x + 1} cycles to {V_fin} volts. Experiment Completed.")
            break
        else:
            job_logger.info(f"The voltage has not stabled after {x + 1} cycles. Continuing experiment."
                f"Analysis result for {x + 1} cycle: {pprint.pformat(cycle_result)}")
            continue
    else:
        # This else statement is executed when the for loop is not terminated by a break statement.
        job_logger.info(f"The voltage has not stabled after {max_cycles} cycles. Experiment Completed.")

