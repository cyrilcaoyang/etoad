import time
from etoad.Utils import ThreadWithReturn
from etoad.Interface.GraphicalInterface import GraphicalInterface

from utils_makeobjects import mk_logger, mk_sampler
"""
    This python script demonstrate the Sampling System.
    A certain volume of sample solution will be diluted with electrolyte solution.
    You have the option to clean up the cell after this.
"""

# ========== Test Settings Below ========== #

sample_name = "H3PO4-addition"

source_port = 12    # The Port from which the Sample will be added.
sample_vol = 2.0       # The volume of sample in mL to be added to the Cell.
wash_line: bool = True     # If True, the line will be washed before the transfer.
start_fresh_sample: bool = False
initial_addition: bool = True  # If True, dead volume will be added to the cell.

enable_gui: bool = False         # GUI can be disabled for simple liquid transfer.

# ========== Test Settings Above ========== #


def liquid_addition(
    logger: GraphicalInterface,
    source_port: int,
    sample_vol: float,
    ini_add: bool = True
):
    sampler = mk_sampler(logger, start_fresh_sample)

    with sampler._atmosphere_handler.open_atmosphere():
        dead_vol = sampler._config["dead_volume"]
        if ini_add:
            sampler.transfer_to_cell(source_port, volume=sample_vol, wash_line=wash_line)
        else:
            sampler.transfer_to_cell(source_port, volume=sample_vol-dead_vol, wash_line=wash_line)
        time.sleep(10)

    sampler.disconnect()
    gui_logger.stop_gui()


if __name__ == "__main__":

    gui_logger = mk_logger(
        task_name="sampler_testing",
        sample_name=sample_name,
        enable_gui=enable_gui
    )
    worker_thread = ThreadWithReturn(
        target=liquid_addition,
        args=(gui_logger, source_port, sample_vol, initial_addition)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()
