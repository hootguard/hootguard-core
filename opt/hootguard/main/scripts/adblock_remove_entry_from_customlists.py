# Script Name: adblock_remove_entry_from_customlists.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script removes URLs from the Pi-hole blacklist or whitelist in the HootGuard system.
# It uses Pi-hole's built-in commands (`pihole -b -d` and `pihole -w -d`) to delete entries 
# from the blacklist or whitelist. The script handles cases where the URL is not found and logs 
# relevant debug information.

import subprocess
from .global_logger import logger

def delete_from_blacklist(urls):
    """Remove URLs from the Pi-hole blacklist."""    
    results = {}
    logger.debug(f"INFO - Deleting URLs from blacklist: {urls}")
    for url in urls:
        try:
            result = subprocess.run(['pihole', '-b', '-d', url], check=True, capture_output=True, text=True)
            results[url] = "deleted"
            logger.debug(f"INFO - URL {url} successfully deleted from blacklist.")
        except subprocess.CalledProcessError as e:
            if "is not in blacklist" in e.stderr:
                results[url] = "not found"
                logger.debug(f"INFO - URL {url} not found in blacklist.")
            else:
                results[url] = f"error: {e.stderr}"
                logger.debug(f"ERROR - Failed to delete URL {url} from blacklist: {str(e)}")
    return results


def delete_from_whitelist(urls):
    """Remove URLs from the Pi-hole whitelist."""
    results = {}
    logger.debug(f"INFO - Deleting URLs from whitelist: {urls}")
    for url in urls:
        try:
            result = subprocess.run(['pihole', '-w', '-d', url], check=True, capture_output=True, text=True)
            results[url] = "deleted"
            logger.debug(f"INFO - URL {url} successfully deleted from whitelist.")
        except subprocess.CalledProcessError as e:
            if "is not in whitelist" in e.stderr:
                results[url] = "not found"
                logger.debug(f"INFO - URL {url} not found in whitelist.")
            else:
                results[url] = f"error: {e.stderr}"
                logger.debug(f"ERROR - Failed to delete URL {url} from whitelist: {str(e)}")
    return results
