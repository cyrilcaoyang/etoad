import time
from utils_makeobjects import mk_logger, mk_sampler


def degas(
    cell_filled: bool,
    degas_time: int = 20
):
    # Instantiate the sampler and start degassing
    gui_logger = mk_logger(
        task_name="degassing",
        sample_name="NaN",
        enable_gui=False
    )

    sampler = mk_sampler(gui_logger, cell_filled)

    with sampler._atmosphere_handler.open_atmosphere():
        time.sleep(degas_time)
    sampler.disconnect()


if __name__ == "__main__":
    degas(False, 20)