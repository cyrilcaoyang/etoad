import test_utils.MakeObjects as MakeObjects
from etoad.Utils import ThreadWithReturn
from Tests.test_utils.LiquidTransfer import wash_cell_refill

"""
This Script is created to empty the EChem Cell and refill with solvent/solution.
    No refill if cell_volume = 0.
"""

# ========== Sample Settings Below ========== #

cell_volume = 10.0              # Wash volume each time
cycles: int = 3                 # How many times the cell will be washed.

# ========== Sample Settings Above ========== #


def wash_cell_drain(
        volume: float = 10.0,
        repeat: int = 3,
) -> None:

    logger = MakeObjects.mk_logger_gui_free(task_name="empty_cell", sample_name="None",)
    logger.debug(f"Emptying the cell and refilling with {volume} mL of solvent/solution.")
    wash_cell_refill(logger, repeat, volume)


if __name__ == "__main__":
    wash_cell_drain(cell_volume, cycles)

