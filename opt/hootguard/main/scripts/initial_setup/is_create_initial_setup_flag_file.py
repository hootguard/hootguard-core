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
