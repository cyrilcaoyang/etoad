from etoad.Utils import ThreadWithReturn
from etoad.Interface.GraphicalInterface import GraphicalInterface
from test_utils.MakeObjects import mk_logger, mk_sampler

"""
This Script is created to empty the EChem Cell and refill with solvent/solution.
    No refill if cell_volume = 0.
"""

# ========== Sample Settings Below ========== #
sample_name = "None"                # Name of the Chemical Solution
wash_volume = 10                     # Wash volume of the cell
refill_volume = 5                   # Refill volume after washing
cycles: int = 3                     # How many times the cell will be washed.

enable_gui = False      # GUI can be disabled for simple liquid transfer.
cell_filled: bool = True           # If the cell is filled, the solution will be drained first.
# ========== Sample Settings Above ========== #


def wash_refill(
        gui_logger: GraphicalInterface,
        wash_vol: float,
        refill_vol: float,
        cycle: int,
) -> None:
    """
    This function will wash the cell and refill it with solvent.
    """

    sampler = mk_sampler(gui_logger, cell_filled)
    sampler.wash_cell(wash_volume=wash_vol, cycles=cycle)
    sampler.transfer_to_cell(source_port=12, volume=refill_vol, wash_line=True)
    sampler.disconnect()


if __name__ == "__main__":

    gui_logger = mk_logger(
        task_name="sampler_testing",
        sample_name=sample_name,
        enable_gui=enable_gui
    )
    worker_thread = ThreadWithReturn(
        target=wash_refill,
        args=(gui_logger, wash_volume, refill_volume, cycles)
    )
    worker_thread.start()
    gui_logger.start_gui()
    worker_thread.join()

