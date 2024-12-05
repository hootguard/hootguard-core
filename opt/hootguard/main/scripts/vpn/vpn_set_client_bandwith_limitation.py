# Script Name: vpn_set_client_bandwidth_limitation.py
# Version: 0.1
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script applies bandwidth limitations to a VPN client using `tc` (traffic control) for both download and upload speeds.
# It determines the client's IP address, applies policing rules for download (egress) and upload (ingress), and updates the bandwidth limits
# in the `temp_vpn_clients` table of the SQLite database.

import subprocess
import sqlite3
from .vpn_get_client_ip_addresses import get_client_ips
#from scripts.global_config import VPN_CLIENTS_DB_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def set_client_bandwidth_limitation(client_name, wg_interface, download_speed, upload_speed):
    """
    Apply bandwidth limits to a VPN client using /usr/local/bin/hootguard.

    :param client_name: The VPN client's name.
    :param wg_interface: The WireGuard interface (e.g., 'wg1').
    :param download_speed: The maximum download speed in Mbits/s.
    :param upload_speed: The maximum upload speed in Mbits/s.
    :return: True if successful, False otherwise.
    """

    # Get IP address of the VPN client (we only need ipv4 - client_ip)
    client_ip, client_ipv6 = get_client_ips(client_name)
    if not client_ip:
        logger.debug(f"ERROR - Could not retrieve IPv4 for client: {client_name}")
        return False

    # Convert rates to kbit for tc
    download_rate = f"{int(download_speed) * 1000}kbit"
    upload_rate = f"{int(upload_speed) * 1000}kbit"

    # Use the last octet of the client's IP for a deterministic classid
    last_octet = client_ip.split('.')[-1]
    flowid_download = f"1:{int(last_octet) + 100}"  # Unique flowid for download
    flowid_upload = f"1:{int(last_octet) + 200}"    # Unique flowid for upload

    try:

        # Call /usr/local/bin/hootguard to set bandwidth limits
        result = subprocess.run(
            [
                '/usr/bin/sudo', '/usr/local/bin/hootguard', 'set-bandwidth',
                wg_interface, client_ip, download_rate, upload_rate, flowid_download, flowid_upload
            ],
            capture_output=True, text=True, check=True
        )

        # Log success
        logger.debug(f"SUCCESS - Bandwidth limits applied for {client_name}: {download_speed} Mbit/s download, {upload_speed} Mbit/s upload on wireguard interface {wg_interface}.")

        # Update the database with the bandwidth limits
        if update_client_bandwidth_limits(client_name, download_speed, upload_speed):
            return True  # Both bandwidth limits and database update successful
        else:
            return False  # Bandwidth limits applied, but database update failed

    except subprocess.CalledProcessError as e:
        logger.debug(f"ERROR - Failed to apply bandwidth limits: {e.stderr}")
        return False
    except Exception as e:
        logger.debug(f"ERROR - Unexpected error while setting bandwidth limits: {e}")
        return False

def update_client_bandwidth_limits(client_name, download_speed, upload_speed):
    """
    Update the download and upload speed in the temp_vpn_clients table for the specified client.

    :param client_name: The VPN client's name.
    :param download_speed: The download speed in Mbits/s.
    :param upload_speed: The upload speed in Mbits/s.
    :return: True if the update was successful, False otherwise.
    """
    try:
        # Connect to the database
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        cursor = conn.cursor()

        # Update the download and upload speed for the client
        cursor.execute('''
            UPDATE temp_vpn_clients
            SET download_speed = ?, upload_speed = ?
            WHERE client_name = ?
        ''', (download_speed, upload_speed, client_name))

        # Commit the transaction and close the connection
        conn.commit()
        conn.close()

        logger.debug(f"SUCCESS - Updated bandwidth limits in the database for {client_name}: {download_speed} Mbit/s download, {upload_speed} Mbit/s upload.")
        return True  # Update successful
    
    except sqlite3.Error as e:
        logger.debug(f"ERROR - Failed to update bandwidth limits in the database for {client_name}: {e}")
        return False  # Update failed
