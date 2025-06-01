# Script Name: adblock_add_entry_to_customlists.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script manages adding URLs to Pi-hole's blacklist and whitelist in the HootGuard system. It uses
# Pi-hole's built-in commands (`pihole -b` and `pihole -w`) to add URLs to the blacklist and whitelist.
# The script also handles cases where the URL is already present in the list and logs relevant debug messages.

import subprocess
from .global_logger import logger

def add_to_blacklist(url):
    try:
        # Add the URL to the Pi-hole blacklist using the pihole -b command
        logger.debug(f"INFO - Adding URL to blacklist: {url}")
        result = subprocess.run(['pihole', '-b', url], check=True, capture_output=True, text=True)
        logger.debug(f"INFO - URL {url} successfully added to blacklist.")
        return "added"
    except subprocess.CalledProcessError as e:
        # Handle the case where the URL is already in the blacklist
        if "already exists" in e.stderr:
            logger.debug(f"INFO - URL {url} already exists in blacklist.")
            return "exists"
        else:
            logger.debug(f"ERROR - Failed to add URL {url} to blacklist: {str(e)}")
            raise

def add_to_whitelist(url):
    try:
        # Add the URL to the Pi-hole whitelist using the pihole -w command
        logger.debug(f"INFO - Adding URL to whitelist: {url}")
        result = subprocess.run(['pihole', '-w', url], check=True, capture_output=True, text=True)
        logger.debug(f"INFO - URL {url} successfully added to whitelist.")
        return "added"
    except subprocess.CalledProcessError as e:
        # Handle the case where the URL is already in the whitelist
        if "already exists" in e.stderr:
            logger.debug(f"INFO - URL {url} already exists in whitelist.")
            return "exists"
        else:
            logger.debug(f"ERROR - Failed to add URL {url} to whitelist: {str(e)}")
            raise
