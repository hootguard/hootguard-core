# Script Name: vpn_main_disable_one_client.py
# Version: 0.1
# Author: HootGuard
# Date: 3. October 2024

# Description:
# This script handles the process of disabling a specific VPN client in the HootGuard system. 
# It performs the following steps:
# 1. Retrieves the client's WireGuard interface (`wg_interface`) and VPN type (`vpn_type`).
# 2. Comments out the client's peer configuration in the WireGuard configuration file.
# 3. Updates the SQLite database to mark the client as deactivated.
# 4. Reloads the WireGuard interface to apply the changes.

# Usage:
# Call the function 'disable_vpn_client(client_name)' to disable a VPN client. The function follows a sequential 
# process to retrieve client information, comment out the peer configuration in the appropriate WireGuard config file, 
# deactivate the client in the database, and reload the WireGuard interface to apply the changes. The function 
# returns True if successful and False if any step fails.

# Change Log:
# 3. October 2024
# Initial version for disabling a VPN client by updating the WireGuard config, database, and reloading the interface.


from .vpn import vpn_get_client_info
from .vpn import vpn_reload_wireguard_config
from .vpn import vpn_deactivate_client_in_db
from .vpn import vpn_comment_out_peer_in_wireguard_interface
from .global_logger import logger

def disable_vpn_client(client_name):
    """Main function to disable a VPN client."""
    
    # Step 1: Get the client info (wg_interface and vpn_type)
    interface, vpn_type = vpn_get_client_info.get_client_info(client_name)
    if not interface or not vpn_type:
        logger.debug(f"Failed to retrieve wg_interface or vpn_type for {client_name}. Exiting.")
        return False

    # Step 2: Comment out the client's configuration in the WireGuard config file
    if not vpn_comment_out_peer_in_wireguard_interface.comment_out_peer_in_wg_config(client_name, interface):
        logger.debug(f"Failed to comment out peer configuration for {client_name}. Exiting.")
        return False

    # Step 3: Update the database to deactivate the client
    if not vpn_deactivate_client_in_db.deactivate_client_in_db(client_name):
        logger.debug(f"Failed to update database for {client_name}. Exiting.")
        return False

    # Step 4: Reload the WireGuard interface
    if not vpn_reload_wireguard_config.vpn_reload_wg_interface(interface):
        logger.debug(f"Failed to reload WireGuard interface {interface}. Exiting.")
        return False

    logger.info(f"VPN client {client_name} disabled successfully.")
    return True