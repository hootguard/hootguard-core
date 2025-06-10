# Script Name: vpn_delete_client_from_db.py
# Version: 0.2
# Author: HootGuard
# Date: 4. October 2024

# Description:
# This script deletes a VPN client's entry from the specified SQLite database table based on the client's name.
# It can be used to remove a client from any table, such as `all_vpn_clients` or `temp_vpn_clients`, by specifying the table name.

# Usage:
# Call the function 'delete_client_from_db(client_name, db_table_name)' with the VPN client's name and the table name as parameters. 
# The function safely formats an SQL query to delete the client record from the specified table in the database. 
# Ensure that 'VPN_CLIENTS_DB_PATH' is correctly set in the global configuration.
# Returns True if the deletion is successful, and False otherwise.

# Change Log:
# 4. October 2024
# Initial version for deleting a VPN client from the database based on client_name and table name.

import sqlite3
#from scripts.global_config import VPN_CLIENTS_DB_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def delete_client_from_db(client_name, db_table_name):
    """Delete the client from the specified table in the database."""
    try:
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        cursor = conn.cursor()

        # Safely format the SQL query to include the table name
        query = f"DELETE FROM {db_table_name} WHERE client_name = ?"

        # Execute the query with the client_name parameter
        cursor.execute(query, (client_name,))
        conn.commit()
        conn.close()

        logger.debug(f"Client {client_name} deleted from {db_table_name}.")
        return True
    except Exception as e:
        logger.debug(f"Failed to delete client {client_name} from {db_table_name}: {str(e)}")
        return False
