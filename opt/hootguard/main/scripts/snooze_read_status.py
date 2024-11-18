# Script Name: snooze_read_status_and_return_status.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script reads the snooze time from a specified file located at `SNOOZE_TIME_FILE_PATH`.
# It returns the snooze time as an integer if the file is found and properly formatted.
# If the file is missing or the value is invalid, it returns `None`. The script includes error
# handling for file not found and value errors.

#from .global_config import SNOOZE_TIME_FILE_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
SNOOZE_TIME_FILE_PATH = config['misc']['snooze_time_file']

def snooze_read_status_and_return_status():
    """Read the snooze time from the snooze file and return it as an integer."""
    logger.debug(f"INFO - Reading snooze time from {SNOOZE_TIME_FILE_PATH}")

    try:
        with open(SNOOZE_TIME_FILE_PATH, 'r') as file:
            snooze_time = file.read().strip()
            snooze_time_int = int(snooze_time)
            logger.debug(f"INFO - Snooze time read successfully: {snooze_time_int}")
            return snooze_time_int
    except FileNotFoundError:
        logger.debug(f"ERROR - Snooze file not found at {SNOOZE_TIME_FILE_PATH}")
        return None
    except ValueError:
        logger.debug(f"ERROR - Invalid snooze time format in {SNOOZE_TIME_FILE_PATH}")
        return None
