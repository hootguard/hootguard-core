# Script Name: vpn_remove_client_bandwidth_limitation.py
# Version: 0.1
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script removes bandwidth limitations and related traffic control (TC) rules for a specific VPN client.
# It retrieves the client's IP address, identifies the traffic control rules applied for both download and upload,
# and deletes the associated egress and ingress rules on the specified WireGuard interface.

import subprocess
import re
from .vpn_get_client_ip_addresses import get_client_ips
#from scripts.global_config import VPN_CLIENTS_DB_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def remove_client_bandwidth_limits(client_name, wg_interface):
    """
    Remove bandwidth limits and related TC rules for a specific VPN client using tc (traffic control) on the specified interface.

    :param client_name: The VPN client's name.
    :param wg_interface: The network interface (e.g., wg0).
    :return: True if successful, False otherwise.
    """

    # Get the IP address of the VPN client
    client_ip, client_ipv6 = get_client_ips(client_name)
    if not client_ip:
        logger.debug(f"Could not retrieve IP for client: {client_name}")
        return False

    # Use the last octet of the client's IP for deterministic flowids
    last_octet = client_ip.split('.')[-1]
    flowid_download = f"1:{int(last_octet) + 100}"  # Flowid used for download (egress)
    flowid_upload = f"1:{int(last_octet) + 200}"    # Flowid used for upload (ingress)

    # Show and store tc rules for egress and ingress in variables
    tc_show_cmd = f"sudo tc filter show dev {wg_interface}"
    tc_show_ingress_cmd = f"sudo tc filter show dev {wg_interface} parent ffff:"

    result = subprocess.run(tc_show_cmd, shell=True, text=True, capture_output=True)
    result_ingress = subprocess.run(tc_show_ingress_cmd, shell=True, text=True, capture_output=True)

    if result.returncode != 0 or result_ingress.returncode != 0:
        logger.debug(f"Error getting tc rules: {result.stderr} {result_ingress.stderr}")
        return False

    # Combine the outputs
    all_rules = result.stdout + result_ingress.stdout

    # Find the handle for the matching flowid (download or upload)
    handle = None
    for line in all_rules.split('\n'):
        if flowid_download in line or flowid_upload in line:
            # Find the handle associated with the flowid
            match = re.search(r'fh ([0-9a-fA-F:]+)', line)
            if match:
                handle = match.group(1)
                logger.debug(f"Found handle for {client_name} (flowid {flowid_download} / {flowid_upload}): {handle}")

    if not handle:
        logger.debug(f"No matching TC rules found for client {client_name}.")
        return False

    # Delete the egress rule (if found)
    if handle:
        delete_egress_cmd = f"sudo tc filter del dev {wg_interface} parent 1: pref 1 handle {handle} u32"
        result = subprocess.run(delete_egress_cmd, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            logger.debug(f"Successfully deleted egress rule for {client_name}.")
        else:
            logger.debug(f"Error deleting egress rule: {result.stderr}")

    # Delete the ingress rule (if found)
    if handle:
        delete_ingress_cmd = f"sudo tc filter del dev {wg_interface} parent ffff: pref 1 handle {handle} u32"
        result_ingress = subprocess.run(delete_ingress_cmd, shell=True, text=True, capture_output=True)
        if result_ingress.returncode == 0:
            logger.debug(f"Successfully deleted ingress rule for {client_name}.")
        else:
            logger.debug(f"Error deleting ingress rule: {result_ingress.stderr}")

    return True
