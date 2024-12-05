# Script Name: adblock_convert_blocking_list.py
# Version: 0.3
# Author: HootGuard
# Date: 4. December 2024

# Description:
# This script converts an Adblock Plus formatted blocking list into a Pi-hole compatible format.
# It retains all comments and reformats domain entries from the Adblock style (`||domain^`)
# to the Pi-hole style (`0.0.0.0 domain`). The script dynamically determines the output file
# path based on the input file name, storing the converted file in a specific directory.
# Unsupported lines are ignored during the conversion process. It also uses a temporary file
# to avoid overwriting the input file during the conversion process.

import os
import tempfile
from .global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Paths from the config
ADBLOCK_CACHE_PATH = config['adblock']['cache_path']


def generate_output_filename(adblock_file):
    """Generates the output file path based on the input file name."""
    # Extract the base name without extension
    filename = os.path.basename(adblock_file)
    name, _ = os.path.splitext(filename)

    # Replace hyphens with underscores for consistency
    output_filename = f"{name.replace('-', '_')}.txt"

    # Combine with the output folder
    return os.path.join(ADBLOCK_CACHE_PATH, output_filename)


def convert_adblock_to_pihole(adblock_file):
    """Converts an Adblock Plus formatted file to a Pi-hole compatible format."""
    try:
        # Verify that the input file exists
        if not os.path.exists(adblock_file):
            logger.error(f"ERROR - File not found: {adblock_file}")
            return False

        logger.debug(f"INFO - Converting file: {adblock_file}")

        # Create a temporary file for output
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file_path = temp_file.name
            logger.debug(f"INFO - Temporary file created: {temp_file_path}")

            # Read from the input file and write converted data to the temporary file
            with open(adblock_file, 'r') as infile:
                for line in infile:
                    line = line.strip()

                    # Keep comments as-is
                    if line.startswith('!'):
                        temp_file.write(f"#{line[1:].strip()}\n")
                    # Convert Adblock domain lines to Pi-hole format
                    elif line.startswith('||') and line.endswith('^'):
                        domain = line[2:-1]  # Extract the domain
                        temp_file.write(f"0.0.0.0 {domain}\n")
                    # Skip any other lines that do not match Adblock syntax
                    else:
                        continue

        # Replace the original file with the converted file
        os.replace(temp_file_path, adblock_file)
        logger.info(f"INFO - Conversion completed. Updated file: {adblock_file}")
        return True

    except Exception as e:
        logger.error(f"ERROR - Error during conversion: {e}")
        return False
