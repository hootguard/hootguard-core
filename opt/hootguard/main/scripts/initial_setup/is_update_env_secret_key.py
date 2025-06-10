# Script Name: is_update_env_secret_key.py
# Version: 0.1
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script generates a new secret key and updates the `.env` file in the HootGuard system. 
# - If the `.env` file exists, the script updates the `SECRET_KEY` entry or appends it if missing.
# - If the `.env` file does not exist, it creates the file and adds the `SECRET_KEY`.
# Logs the success or failure of the operation and ensures secure management of the secret key.
# Returns `True` if successful, `False` otherwise.

import os
import secrets
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Define the path where WireGuard configuration files are stored
ENV_FILE_PATH = config['misc']['env_file_path']

def generate_and_update_secret_key(key_length=50):
    """Generates a new secret key and updates the .env file with it. Returns True if successful, False otherwise."""
    try:
        # Generate a new secret key
        secret_key = secrets.token_urlsafe(key_length)

        # Check if the .env file exists, if not, create it
        if not os.path.exists(ENV_FILE_PATH):
            # Create the file and add the SECRET_KEY
            with open(ENV_FILE_PATH, 'w') as file:
                file.write(f"SECRET_KEY={secret_key}\n")
        else:
            # Read the existing .env file
            with open(ENV_FILE_PATH, 'r') as file:
                lines = file.readlines()

            # Update or append the SECRET_KEY
            secret_key_exists = False
            with open(ENV_FILE_PATH, 'w') as file:
                for line in lines:
                    if line.startswith('SECRET_KEY'):
                        file.write(f"SECRET_KEY={secret_key}\n")
                        secret_key_exists = True
                    else:
                        file.write(line)
                # If SECRET_KEY was not found, append it
                if not secret_key_exists:
                    file.write(f"SECRET_KEY={secret_key}\n")

        logger.debug(f"New SECRET_KEY generated and added to {ENV_FILE_PATH}")
        return True

    except Exception as e:
        logger.debug(f"Error occurred: {e}")
        return False
