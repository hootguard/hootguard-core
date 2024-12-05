# Script Name: is_update_password_secret_key.py
# Version: 0.1
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script generates a new Fernet secret key and replaces the existing password secret key file in the HootGuard system.
# - If the secret key file does not exist, it creates the necessary directory and an empty file.
# - Replaces the content of the key file with a newly generated Fernet key.
# Logs the success or failure of the operation to ensure secure handling of password encryption keys.
# Returns `True` if successful, `False` otherwise.

import os
from cryptography.fernet import Fernet
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Define the path where WireGuard configuration files are stored
KEY_FILE_PATH = config['passwords']['secret_key_path']

# Function to generate and replace the secret key
def generate_and_replace_secret_key():
    try:
        # Check if the file exists, if not, create an empty file
        if not os.path.exists(KEY_FILE_PATH):
            # Ensure that the directory exists
            os.makedirs(os.path.dirname(KEY_FILE_PATH), exist_ok=True)
            
            # Create the file if it does not exist
            with open(KEY_FILE_PATH, "wb") as key_file:
                pass  # Creates an empty file

        # Generate a new Fernet secret key
        new_key = Fernet.generate_key()

        # Replace the existing secret key file with the new key
        with open(KEY_FILE_PATH, "wb") as key_file:
            key_file.write(new_key)

        logger.debug(f"New secret key generated and saved to {KEY_FILE_PATH}")
        return True
    except Exception as e:
        logger.debug(f"Error occurred: {e}")
        return False

#if __name__ == "__main__":
#    success = generate_and_replace_secret_key()
