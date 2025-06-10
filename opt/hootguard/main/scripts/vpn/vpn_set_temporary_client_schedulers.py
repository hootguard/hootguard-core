# Script Name: vpn_set_temporary_client_schedulers.py
# Version: 0.1
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script schedules the activation and deactivation of a temporary VPN client. It uses the `apscheduler` library 
# to schedule start and end times for the VPN client and optionally deletes the client after the deactivation if 
# automatic deletion is enabled. The scheduling details are also stored in the `temp_vpn_clients` table in the SQLite database.

import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from scripts.vpn_main_enable_one_client import enable_vpn_client
from scripts.vpn_main_disable_one_client import disable_vpn_client
#from scripts.global_config import VPN_CLIENTS_DB_PATH, VPN_CONFIGS_PATH
from scripts.vpn_main_remove_one_client import remove_vpn_client
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']
VPN_CONFIGS_PATH = config['vpn']['client_configs_path']


# Initialize the scheduler
scheduler = BackgroundScheduler()

def set_vpn_client_scheduler(client_name, start_time, end_time, automatic_deletion):
    """
    Schedule the activation and deactivation of a VPN client.

    :param client_name: The VPN client's name
    :param start_time: The time to activate the VPN client (ISO format)
    :param end_time: The time to deactivate the VPN client (ISO format)
    :param automatic_deletion: Boolean indicating if the client should be deleted after deactivation
    :return: True if scheduling was successful, False otherwise
    """
    try:
        # Convert start and end times to datetime objects
        start_time_dt = datetime.fromisoformat(start_time)
        end_time_dt = datetime.fromisoformat(end_time)

        # Store the schedule in the database
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO temp_vpn_clients (client_name, start_time, end_time, automatic_deletion) VALUES (?, ?, ?, ?)',
                  (client_name, start_time, end_time, automatic_deletion))
        conn.commit()
        conn.close()

        # Schedule the activation and deactivation
        scheduler.add_job(enable_vpn_client, 'date', run_date=start_time_dt, args=[client_name])
        scheduler.add_job(disable_vpn_client, 'date', run_date=end_time_dt, args=[client_name])

        # If the user activated the automatic VPN client deletion after the temp client time is over
        if automatic_deletion:
            scheduler.add_job(remove_vpn_client, 'date', run_date=end_time_dt, args=[client_name])

        logger.debug(f"SUCCESS - Successfully scheduled VPN client {client_name}")
        return True

    except sqlite3.Error as e:
        logger.debug(f"ERROR - Failed to store schedule in the database for client {client_name}: {e}")
        return False

    except Exception as e:
        logger.debug(f"ERROR - An unexpected error occurred while scheduling VPN client {client_name}: {e}")
        return False

# Start the scheduler
scheduler.start()
