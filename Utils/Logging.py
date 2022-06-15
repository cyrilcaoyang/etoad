import logging
import logging.config
from pathlib import Path
from typing import Union

from .ConfigLoader import ConfigLoader


def get_logger(config_file: Path, logger_name: str, logfile: Union[Path, None] = None) -> logging.Logger:
    """
    Configures the logging module according to the logging configurations.
    Returns a Logger object that can be passed to the different classes.

    Args:
        config_file: Path to the logger configuration file.
        logger_name: Name of the logger type (as specified in the configuration file).
        logfile: Path to the log file (optional, otherwise default from config is used).

    Returns:
        Logger object with the configurations as given in the config file.
    """
    config = ConfigLoader.load_config(config_file)

    if logfile:
        config["handlers"]["file"]["filename"] = str(logfile)

    logging.config.dictConfig(config)
    return logging.getLogger(logger_name)
