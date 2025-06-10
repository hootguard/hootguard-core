# Script Name: vpn_main_remove_one_client.py
# Version: 0.4
# Author: HootGuard
# Date: 6. October 2024

# Description:
# This script orchestrates the removal of an existing WireGuard VPN client from the HootGuard system. 
# It performs several key steps, including deleting the client configuration file, removing the peer 
# configuration from the appropriate WireGuard interface configuration file (wg0 or wg1), removing the client 
# record from both the `all_vpn_clients` and `temp_vpn_clients` tables (if applicable), deleting the client's 
# traffic control bandwidth limits, removing the client's keys and QR code file, and finally reloading the 
# WireGuard interface to apply the changes.

from .vpn import vpn_remove_client_config
from .vpn import vpn_remove_peer_from_wg_config
from .vpn import vpn_delete_client_from_db
from .vpn import vpn_get_client_info
from .vpn import vpn_remove_client_keys
from .vpn import vpn_remove_qr_code_file
from .vpn import vpn_reload_wireguard_config
from .vpn import vpn_remove_client_bandwith_limitation
from .global_logger import logger

def remove_vpn_client(client_name):
    """Main function to remove a VPN client from the system."""

    # Step 1: Get wg_interface and vpn_type from the database
    interface, vpn_type = vpn_get_client_info.get_client_info(client_name)
    if not interface or not vpn_type:
        logger.debug(f"Failed to retrieve wg_interface or vpn_type for {client_name}. Exiting.")
        return False

    # Step 2: Remove client configuration file
    logger.debug(f"Removing client configuration file for {client_name}...")
    if not vpn_remove_client_config.remove_client_config(client_name):
        logger.debug(f"Failed to remove client configuration file for {client_name}.")
        return False

    # Step 3: Remove peer configuration from the WireGuard interface config file
    logger.debug(f"Removing peer configuration for {client_name} from {interface} config file...")
    if not vpn_remove_peer_from_wg_config.remove_peer_from_wg_config(client_name, interface):
        logger.debug(f"Failed to remove peer configuration for {client_name} from {interface} config file.")
        return False

    # Step 4.1: Only for temporary vpn clients (time_limited / full_limited)
    # Delete client record from the database - table: temp_vpn_clients
    # The sequence 4.1 before 4.2 must be observed as the scripts in 4.1 access the data in the database that is deleted in 4.2.
    if vpn_type == "time_limited" or vpn_type == "full_limited":
        logger.debug(f"Deleting temporary client {client_name} from database...")
        if not vpn_delete_client_from_db.delete_client_from_db(client_name, "temp_vpn_clients"):
            logger.debug(f"Failed to delete client {client_name} from the database.")
            return False
        # 4.2.1 Only for full_limited vpn clients (bandwith limited)
        # Delete traffic control bandwith limitation for temporary vpn client
        if vpn_type == "full_limited":
            logger.debug(f"Deleting temporary client {client_name} from database...")
            if not vpn_remove_client_bandwith_limitation.remove_client_bandwidth_limits(client_name, interface):
                logger.debug(f"Failed to remove bandwidth limits for {client_name}")
                return False

    # Step 4.2: Delete client record from the database - table: all_vpn_clients
    logger.debug(f"Deleting client {client_name} from database...")
    if not vpn_delete_client_from_db.delete_client_from_db(client_name, "all_vpn_clients"):
        logger.debug(f"Failed to delete client {client_name} from the database.")
        return False

    # Step 5: Remove client keys
    logger.debug(f"Removing client keys for {client_name}...")
    if not vpn_remove_client_keys.remove_client_keys(client_name):
        logger.debug(f"Failed to remove keys for {client_name}.")
        return False

    # Step 6: Remove the QR code file
    logger.debug(f"Removing QR code file for {client_name}...")
    if not vpn_remove_qr_code_file.remove_qr_code(client_name):
        logger.debug(f"Failed to remove QR code file for {client_name}.")
        return False

    # Step 7: Reload the WireGuard server config to apply the changes
    logger.debug(f"Reloading WireGuard configuration for interface: {interface}...")
    if not vpn_reload_wireguard_config.vpn_reload_wg_interface(interface):
        logger.debug(f"Failed to reload WireGuard configuration for {interface}.")
        return False
    logger.debug(f"WireGuard configuration for {interface} reloaded successfully.")

    logger.info(f"VPN client {client_name} removed successfully.")
    return True

