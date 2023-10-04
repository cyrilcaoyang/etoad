import time
from etoad.Utils import ThreadWithReturn
from etoad.Interface.GraphicalInterface import GraphicalInterface

from test_utils.MakeObjects import mk_logger, mk_sampler
"""
    This python script demonstrate the Sampling System.
    A certain volume of sample solution will be diluted with electrolyte solution.
    You have the option to clean up the cell after this.
"""

# ========== Test Settings Below ========== #

sample_name = "HCl-addition"

source_port = 5     # The Port from which the Sample will be added.
sample_vol = 0.4        # The volume of sample in mL to be added to the Cell.
wash_line: bool = False      # If True, the wash line will be used to transfer the sample.
start_fresh_sample: bool = False

enable_gui: bool = False         # GUI can be disabled for simple liquid transfer.

# ========== Test Settings Above ========== #


def liquid_addition(
    logger: GraphicalInterface,
    source_port: int,
    sample_vol: float
):
    sampler = mk_sampler(logger, start_fresh_sample)

    with sampler._atmosphere_handler.open_atmosphere():
        sampler.transfer_to_cell(source_port, volume=sample_vol, wash_line=wash_line)
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
        args=(gui_logger, source_port, sample_vol)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()




