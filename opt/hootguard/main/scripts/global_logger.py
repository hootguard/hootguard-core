# Script Name: global_logger.py
# Version: 0.2
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script configures the global logging system for the HootGuard project. It sets up a logger named 'HGLog'
# and configures it to write logs to a specified file. The logging format includes the timestamp, log level, 
# script/module name, and the log message. The logger is used across various HootGuard scripts to provide 
# consistent logging and debugging information.

import logging
import os
#from .global_config import HOOTGUARD_GLOBAL_LOGGING_FILE_PATH
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
log_level = config['logging']['level'].upper()
HOOTGUARD_GLOBAL_LOGGING_FILE_PATH = config['logging']['global_logging_file_path']

# Configure logging
logger = logging.getLogger('HGLog')
logger.setLevel(getattr(logging, log_level, logging.INFO))

# Ensure the logger does not propagate to the root logger
logger.propagate = False

# Create a file handler
file_handler = logging.FileHandler(HOOTGUARD_GLOBAL_LOGGING_FILE_PATH)
file_handler.setLevel(getattr(logging, log_level, logging.INFO))

# Create a logging format that includes the script/module name
formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s - %(module)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Optionally, add a console handler to also output logs to the console (for development/debugging)
console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, log_level, logging.INFO))  # Set console handler log level dynamically
console_handler.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(console_handler)
