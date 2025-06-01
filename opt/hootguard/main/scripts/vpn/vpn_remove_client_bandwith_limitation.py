# Script Name: vpn_remove_client_bandwidth_limitation.py
# Version: 0.1
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script removes bandwidth limitations and related traffic control (TC) rules for a specific VPN client.
# It retrieves the client's IP address, identifies the traffic control rules applied for both download and upload,
# and deletes the associated egress and ingress rules on the specified WireGuard interface.

import subprocess
from .vpn_get_client_ip_addresses import get_client_ips
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def remove_client_bandwidth_limits(client_name, wg_interface):
    """
    Remove bandwidth limits for a specific VPN client using /usr/local/bin/hootguard.

    :param client_name: The VPN client's name.
    :param wg_interface: The network interface (e.g., wg0).
    :return: True if successful, False otherwise.
    """
    # Get the client's IP address
    client_ip, _ = get_client_ips(client_name)
    if not client_ip:
        logger.debug(f"Could not retrieve IP for client: {client_name}")
        return False

    # Calculate deterministic flowids based on the last octet of the IP
    last_octet = client_ip.split('.')[-1]
    flowid_download = f"1:{int(last_octet) + 100}"
    flowid_upload = f"1:{int(last_octet) + 200}"

    try:
        # Call /usr/local/bin/hootguard to remove bandwidth limits
        result = subprocess.run(
            [
                '/usr/bin/sudo', '/usr/local/bin/hootguard', 'remove-bandwidth',
                wg_interface, client_ip, flowid_download, flowid_upload
            ],
            capture_output=True, text=True, check=True
        )

        logger.debug(f"Successfully removed bandwidth limits for {client_name}. Output: {result.stdout}")
        return True

    except subprocess.CalledProcessError as e:
        logger.debug(f"Failed to remove bandwidth limits for {client_name}: {e.stderr}")
        return False
