# Script Name: vpn_remove_limited_client_from_temp_database.py
# Version: 0.1
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script removes a VPN client from the `temp_vpn_clients` table in the SQLite database. 
# It deletes the client record based on the client name provided and handles any exceptions during the deletion process.

import sqlite3
#from .global_config import VPN_CLIENTS_DB_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def remove_from_temp_database(client_name):
    """
    Delete an existing VPN client and its associated QR code non-interactively by automatically confirming.
    Also removes the client from the database storing temporary VPN clients.

    :param client_name: The name of the VPN client to delete
    :return: True if successful, False otherwise
    """
    try:
        # Remove the client from the database
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM temp_vpn_clients WHERE client_name = ?', (client_name,))
        conn.commit()
        conn.close()

        logger.debug(f"SUCCESS - Temporary client {client_name} successfully from database removed.")
        return True
    except subprocess.CalledProcessError as e:
        logger.debug(f"ERROR - Error deleting VPN client: {e}")
        return False
    except OSError as e:
        logger.debug(f"ERROR - Error deleting QR code file: {e}")
        return False
