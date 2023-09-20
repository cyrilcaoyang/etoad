import test_utils.MakeObjects as MakeObjects
from etoad.Utils import ThreadWithReturn
from Tests.test_utils.LiquidTransfer import wash_cell_refill

"""
This Script is created to empty the EChem Cell and refill with solvent/solution.
"""

# ========== Sample Settings Below ========== #

cycles: int = 3                 # How many times the cell will be washed.
cell_volume = 10.0               # Wash volume each time
enable_gui: bool = False        # We are disabling GUI for simple cell washing.

# ========== Sample Settings Above ========== #


def wash_cell_drain(
        volume: float = 10.0,
        repeat: int = 3,
        gui: bool = False
) -> None:
    gui_logger = MakeObjects.mk_logger(
        task_name="empty_cell",
        sample_name="None",
        enable_gui=gui
    )

    worker_thread = ThreadWithReturn(
        target=wash_cell_refill,
        args=(gui_logger, repeat, volume)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()


if __name__ == "__main__":
    wash_cell_drain(cell_volume, cycles, enable_gui)

