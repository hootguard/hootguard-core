# Script Name: vpn_get_temp_client_details.py
# Version: 0.2
# Author: HootGuard
# Date: 4. October 2024

# Description:
# This script retrieves details for temporary VPN clients from the HootGuard SQLite database. 
# It provides functions to fetch a temporary client's download and upload speeds, automatic deletion status, 
# and start and end times. The data retrieved is formatted for easy display, particularly in the case of time values.

import sqlite3
from datetime import datetime
#from .global_config import VPN_CLIENTS_DB_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def vpn_get_temp_speeds(username):
    """
    Get the download and upload speed for a temporary VPN client.

    :param username: The VPN client's username
    :return: Tuple containing download_speed and upload_speed if found, otherwise (None, None)
    """
    try:
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT download_speed, upload_speed FROM temp_vpn_clients WHERE client_name=?", (username,))
        result = c.fetchone()
        conn.close()

        if result:
            download_speed, upload_speed = result
            # Handle None values for optional speeds
            download_speed = download_speed if download_speed is not None else 0
            upload_speed = upload_speed if upload_speed is not None else 0
            return download_speed, upload_speed
    except Exception as e:
        logger.debug(f"Error retrieving speeds for {username}: {e}")
    return None, None

def vpn_get_automatic_deletion(username):
    """
    Get the automatic deletion status for a temporary VPN client.

    :param username: The VPN client's username
    :return: 'On' if automatic_deletion is 1, 'Off' if it's 0, otherwise None
    """
    try:
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT automatic_deletion FROM temp_vpn_clients WHERE client_name=?", (username,))
        result = c.fetchone()
        conn.close()

        if result:
            automatic_deletion = result[0]
            return "On" if automatic_deletion == 1 else "Off"
    except Exception as e:
        logger.debug(f"Error retrieving deletion status for {username}: {e}")
    return None

def vpn_get_temp_start_end_time(username):
    """
    Get the start and end time for a temporary VPN client and format them for display.

    :param username: The VPN client's username
    :return: Tuple containing formatted start_time and end_time if found, otherwise (None, None)
    """
    try:
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        c = conn.cursor()
        c.execute("SELECT start_time, end_time FROM temp_vpn_clients WHERE client_name=?", (username,))
        result = c.fetchone()
        conn.close()
        
        if result:
            start_time, end_time = result
            # Ensure that start_time and end_time are not None
            if start_time:
                start_time = datetime.fromisoformat(start_time).strftime("%d. %B %Y %H:%M")
            if end_time:
                end_time = datetime.fromisoformat(end_time).strftime("%d. %B %Y %H:%M")
            return start_time, end_time
    except Exception as e:
        logger.debug(f"Error retrieving times for {username}: {e}")
    return None, None
