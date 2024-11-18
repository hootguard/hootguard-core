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
    Apply bandwidth limits to a VPN client using tc (traffic control) on wg1.

    :param client_name: The VPN client's name.
    :param download_speed: The maximum download speed in Mbits/s.
    :param upload_speed: The maximum upload speed in Mbits/s.
    """

    # Get IP address of the VPN client (we only need ipv4 - client_ip)
    client_ip, client_ipv6 = get_client_ips(client_name)
    if not client_ip:
        logger.debug(f"ERROR - Could not retrieve IPv4 for client: {client_name}")
        return False

    # Convert rates to kbit for tc
    download_rate = f"{int(download_speed) * 1000}kbit"
    upload_rate = f"{int(upload_speed) * 1000}kbit"
    burst_size = '100k'  # Increase burst size for upload control

    # Use the last octet of the client's IP for a deterministic classid
    last_octet = client_ip.split('.')[-1]
    flowid_download = f"1:{int(last_octet) + 100}"  # Unique flowid for download
    flowid_upload = f"1:{int(last_octet) + 200}"    # Unique flowid for upload

    try:

        # Step 1.1: Check if the root qdisc already exists, if it exists, do nothing, if it does not exits, add it.
        root_qdisc_exists = subprocess.run(['sudo', 'tc', 'qdisc', 'show', 'dev', wg_interface], capture_output=True, text=True)
        if 'fq_codel' not in root_qdisc_exists.stdout:
            # If root qdisc does not exist, add it
            subprocess.run(['sudo', 'tc', 'qdisc', 'add', 'dev', wg_interface, 'root', 'handle', '1:', 'fq_codel'], check=True)

        # Step 1.2: Apply policing to limit download traffic (egress)
        # Policing based on destination IP (client's IP)
        egress_commands = [
            ['sudo', 'tc', 'filter', 'add', 'dev', wg_interface, 'protocol', 'ip', 'parent', '1:', 'prio', '1', 'u32',
             'match', 'ip', 'dst', client_ip, 'police', 'rate', download_rate, 'burst', burst_size, 'drop', 'flowid', flowid_download]
        ]

        # Step 2.1: Check if the ingress qdisc exists
        ingress_qdisc_exists = subprocess.run(['sudo', 'tc', 'qdisc', 'show', 'dev', wg_interface], capture_output=True, text=True)
        if 'ingress' not in ingress_qdisc_exists.stdout:
            # If ingress qdisc does not exist, add it
            subprocess.run(['sudo', 'tc', 'qdisc', 'add', 'dev', wg_interface, 'handle', 'ffff:', 'ingress'])

        # Step 2.2: Apply policing to limit upload traffic (ingress)
        ingress_commands = [
            # Policing based on source IP (client's IP)
            ['sudo', 'tc', 'filter', 'add', 'dev', wg_interface, 'parent', 'ffff:', 'protocol', 'ip', 'prio', '1', 'u32',
             'match', 'ip', 'src', client_ip, 'police', 'rate', upload_rate, 'burst', burst_size, 'drop', 'flowid', flowid_upload]
        ]

        # Execute the commands for download limiting (egress)
        for cmd in egress_commands:
            subprocess.run(cmd, check=True)

        # Execute the commands for upload limiting (egress) and ingress policing
        for cmd in ingress_commands:
            subprocess.run(cmd, check=True)

        logger.debug(f"SUCCESS - Bandwidth limits applied for {client_name}: {download_speed} Mbit/s download, {upload_speed} Mbit/s upload on wireguard interface {wg_interface}.")

        # Update the database with the bandwidth limits
        if update_client_bandwidth_limits(client_name, download_speed, upload_speed):
            return True  # Both bandwidth limits and database update successful
        else:
            return False  # Bandwidth limits applied, but database update failed

    except subprocess.CalledProcessError as e:
        logger.debug(f"ERROR - Failed to apply bandwidth limits: {e}")
        return False
    return True


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
