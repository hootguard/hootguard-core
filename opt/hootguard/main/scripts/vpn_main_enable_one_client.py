# Script Name: vpn_main_enable_one_client.py
# Version: 0.7
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script is used to enable a previously disabled VPN client in the HootGuard system. 
# It performs the following steps:
# 1. Retrieves the client's WireGuard interface (`wg_interface`) and VPN type (`vpn_type`).
# 2. Uncomments the client's peer configuration in the WireGuard configuration file.
# 3. Updates the SQLite database to mark the client as enabled.
# 4. Reloads the WireGuard interface to apply the changes.

from .vpn import vpn_get_client_info
from .vpn import vpn_reload_wireguard_config
from .vpn import vpn_enable_client_in_db
from .vpn import vpn_uncomment_peer_in_wireguard_interface
from .global_logger import logger

def enable_vpn_client(client_name):
    """Main function to enable a VPN client."""
    
    # Step 1: Get the client info (wg_interface and vpn_type)
    interface, vpn_type = vpn_get_client_info.get_client_info(client_name)
    if not interface or not vpn_type:
        logger.debug(f"Failed to retrieve wg_interface or vpn_type for {client_name}. Exiting.")
        return False

    # Step 2: Uncomment the client's configuration in the WireGuard config file
    if not vpn_uncomment_peer_in_wireguard_interface.uncomment_peer_in_wg_config(client_name, interface):
        logger.debug(f"Failed to uncomment peer configuration for {client_name}. Exiting.")
        return False

    # Step 3: Update the database to enable the client
    if not vpn_enable_client_in_db.enable_client_in_db(client_name):
        logger.debug(f"Failed to update database for {client_name}. Exiting.")
        return False

    # Step 4: Reload the WireGuard interface
    if not vpn_reload_wireguard_config.vpn_reload_wg_interface(interface):
        logger.debug(f"Failed to reload WireGuard interface {interface}. Exiting.")
        return False

    logger.info(f"VPN client {client_name} enabled successfully.")
    return True
