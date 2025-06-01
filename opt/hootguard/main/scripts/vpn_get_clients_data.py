# Script Name: vpn_get_clients_data.py
# Version: 0.2
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script retrieves data about VPN clients from the HootGuard SQLite database. It gathers information 
# about active VPN clients, disabled VPN clients, and temporary VPN clients (classified as either 
# 'time_limited' or 'full_limited'). The data is returned in a structured format, where each client is 
# represented by their name. The script processes data for different client types and returns the lists 
# accordingly.

import sqlite3
#from .global_config import VPN_CLIENTS_DB_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def get_vpn_clients_data():
    # Connect to the SQLite database
    conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
    conn.row_factory = sqlite3.Row  # To get dictionary-like access to the rows
    cur = conn.cursor()

    # Query for active clients (vpn_status = 1)
    query_active = """
    SELECT client_name FROM all_vpn_clients WHERE vpn_status = 1
    """
    cur.execute(query_active)
    active_rows = cur.fetchall()

    # Query for disabled clients (vpn_status = 0)
    query_disabled = """
    SELECT client_name FROM all_vpn_clients WHERE vpn_status = 0
    """
    cur.execute(query_disabled)
    disabled_rows = cur.fetchall()

    # Query for temporary clients (vpn_type = 'time_limited' or 'full_limited')
    query_temp = """
    SELECT client_name FROM all_vpn_clients WHERE vpn_type IN ('time_limited', 'full_limited')
    """
    cur.execute(query_temp)
    temp_rows = cur.fetchall()

    # Process the active clients
    active_clients = []
    for row in active_rows:
        client = {
            'name': row['client_name'],
        }
        active_clients.append(client)

    # Process the disabled clients
    disabled_clients = []
    for row in disabled_rows:
        client = {
            'name': row['client_name'],
        }
        disabled_clients.append(client)

    # Process the temp clients
    temp_clients = []
    temp_clients_names = []
    for row in temp_rows:
        client = {
            'client_name': row['client_name'],
        }
        temp_clients.append(client)
        temp_clients_names.append(row['client_name'])  # Store just the client names

    # Close the database connection
    conn.close()

    # Return the structured data
    logger.debug("Clients data was successfully retreived")
    return active_clients, disabled_clients, temp_clients, temp_clients_names
