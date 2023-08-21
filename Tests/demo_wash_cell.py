import test_utils.MakeObjects as MakeObjects

from etoad.Interface import GraphicalInterface
from etoad.Utils import ThreadWithReturn

"""
This Script is created to wash the EChem Cell.
"""

# ========== Sample Settings Below ========== #

REPEAT: int = 3                 # How many times the cell will be washed.
WASH_VOLUME = 5.0               # Wash volume each time
DISABLE_GUI: bool = True        # We are disabling GUI for simple cell washing.

# ========== Sample Settings Above ========== #


def wash_cell(
        repeat: int,
        wash_volume: float,
        logger: GraphicalInterface
) -> None:

    sampler = MakeObjects.mk_sampler(logger=logger)
    sampler.wash_cell(repeat)
    sampler.transfer_to_cell(source_port=12, volume=wash_volume, wash_line=True)


if __name__ == "__main__":

    gui_logger = MakeObjects.mk_logger(
        task_name="wash_cell",
        sample_name="CELL_WASH",
        disable_gui=DISABLE_GUI
    )

    worker_thread = ThreadWithReturn(
        target=wash_cell, args=(REPEAT, WASH_VOLUME, gui_logger)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()

