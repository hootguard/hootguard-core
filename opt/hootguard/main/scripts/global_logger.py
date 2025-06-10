# Script Name: global_logger.py
# Version: 0.3
# Author: HootGuard
# Date: 24. November 2024

# Description:
# This script configures the global logging system for the HootGuard project. It sets up a logger named 'HGLog'
# and configures it to write logs to a specified file. The logging format includes the timestamp, log level, 
# script/module name, and the log message. The logger is used across various HootGuard scripts to provide 
# consistent logging and debugging information.

import logging
import os
from logging.handlers import RotatingFileHandler
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
log_level = config['logging'].get('level', 'INFO').upper()
HOOTGUARD_GLOBAL_LOGGING_FILE_PATH = config['logging']['global_logging_file_path']

# Configure logging
logger = logging.getLogger('HGLog')
logger.setLevel(log_level)
logger.propagate = False  # Prevent logs from propagating to the root logger

# Ensure the log directory exists
log_dir = os.path.dirname(HOOTGUARD_GLOBAL_LOGGING_FILE_PATH)
os.makedirs(log_dir, exist_ok=True)

# Add a RotatingFileHandler
try:
    file_handler = RotatingFileHandler(
        HOOTGUARD_GLOBAL_LOGGING_FILE_PATH,
        maxBytes=10 * 1024 * 1024,  # 10 MB max
        backupCount=5  # Keep up to 5 backups
    )
    file_handler.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s - %(module)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(file_handler)
except (IOError, PermissionError) as e:
    print(f"Warning: Unable to write to log file {HOOTGUARD_GLOBAL_LOGGING_FILE_PATH}. Falling back to console logging.")

# Add a console handler (for development/debugging)
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
console_handler.setFormatter(formatter)
if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    logger.addHandler(console_handler)
