# Script Name: is_create_initial_setup_flag_file.py
# Version: 0.1
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script creates an initialization flag file to indicate the successful completion of the initial setup process.
# It retrieves the file path from the global configuration and writes a confirmation message to the file.
# The script logs the success or failure of the file creation operation and returns a status accordingly.

import os
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

def create_init_flag():
    # Define the file path
    flag_file_path = config['misc']['init_flag']

    # Create the file
    try:
        with open(flag_file_path, 'w') as flag_file:
            flag_file.write('Initialization flag created.\n')
        logger.info(f"File '{flag_file_path}' has been created successfully.")
        return True
    except Exception as e:
        logger.error(f"Error creating the file: {e}")
        return False
