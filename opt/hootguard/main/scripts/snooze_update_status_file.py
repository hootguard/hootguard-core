# Script Name: snooze_update_time.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script updates the snooze time by writing a new snooze value to the specified file at `SNOOZE_TIME_FILE_PATH`.
# If the operation is successful, it logs the updated value and returns `True`. If an error occurs during the file 
# writing process, it logs the error and returns `False`.

#from .global_config import SNOOZE_TIME_FILE_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
SNOOZE_TIME_FILE_PATH = config['misc']['snooze_time_file']

def snooze_update_time(new_snooze_time):
    """Update the snooze time by writing the new value to the snooze file."""
    logger.debug(f"INFO - Updating snooze time to {new_snooze_time}")

    try:
        with open(SNOOZE_TIME_FILE_PATH, 'w') as file:
            file.write(str(new_snooze_time))
        logger.info(f"Successfully updated snooze time to {new_snooze_time}")
        return True
    except Exception as e:
        logger.error(f"Error occurred while updating snooze time: {e}")
        return False
