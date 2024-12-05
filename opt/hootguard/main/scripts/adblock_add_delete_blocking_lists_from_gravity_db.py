# Script Name: adblock_add_delete_blocking_lists_from_gravity_db.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script adds or removes blocking lists from the Pi-hole gravity database used by the HootGuard system.
# It performs several key steps, including clearing existing entries from the `adlist` table in the Pi-hole
# database, adding new blocking lists based on specified profiles, and updating gravity afterward. It uses
# the global configuration for database paths and blocklist URLs.

import sqlite3
import subprocess
from .adblock_update_gravity_db import update_gravity_db
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config 
config = load_config()

# Access configuration values
ADBLOCK_DB_PATH = config['adblock']['db_path']
ADBLOCK_BLOCKLIST_URLS = config['adblock']['blocklist_urls']

def adblock_add_blocking_list(profiles):
    """Add new blocking lists to the Pi-hole database for each profile in the list and update gravity."""
    success = True
    logger.debug(f"INFO - Adding blocking lists for profiles: {profiles}")

    try:
        with sqlite3.connect(ADBLOCK_DB_PATH) as conn:
            cur = conn.cursor()
            # Clear all existing entries from adlist before adding new ones
            logger.debug("INFO - Deleting all existing entries from adlist table.")
            cur.execute("DELETE FROM adlist;")

            for profile in profiles:
                url = ADBLOCK_BLOCKLIST_URLS.get(profile)
                if url:
                    cur.execute("INSERT OR IGNORE INTO adlist (address) VALUES (?);", (url,))
                else:
                    logger.debug(f"ERROR - No URL defined for '{profile}'. Skipping.")
                    continue

            conn.commit()
    except sqlite3.DatabaseError as e:
        logger.debug(f"ERROR - Database error while updating blocking lists: {str(e)}")
        success = False
    except Exception as e:
        logger.debug(f"ERROR - Unexpected error: {str(e)}")
        success = False

    if success:
        success = update_gravity_db()

    return success
