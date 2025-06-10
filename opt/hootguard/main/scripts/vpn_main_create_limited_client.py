# Script Name: vpn_main_create_limited_client.py
# Version: 0.5
# Author: HootGuard
# Date: 5. October 2024

# Description:
# This script is responsible for creating temporary VPN clients with either time limits or both time and bandwidth limits.
# It allows for the creation of two types of limited clients:
# 1. Time-limited VPN clients (without bandwidth limitations)
# 2. Fully limited VPN clients (with both time and bandwidth limitations)
# The created clients are automatically deactivated after creation, regardless of the success or failure of the process.

from .vpn_main_create_unlimited_client import create_vpn_client
from .vpn_main_disable_one_client import disable_vpn_client
from .vpn import vpn_set_temporary_client_schedulers
from .vpn import vpn_set_client_bandwith_limitation
from .global_logger import logger

def create_limited_vpn_client(client_name, start_time, end_time, auto_deletion, download_speed=None, upload_speed=None):
    # VPN is by default deactivated (0) for temporary clients
    vpn_status = 0
    try:
        # Create a time and bandwidth limited (full limited) VPN client
        if download_speed and upload_speed:
            wg_interface = "wg1"
            vpn_type = "full_limited"
            if create_vpn_client(client_name, wg_interface, vpn_status, vpn_type):
                if vpn_set_temporary_client_schedulers.set_vpn_client_scheduler(client_name, start_time, end_time, auto_deletion):
                    if vpn_set_client_bandwith_limitation.set_client_bandwidth_limitation(client_name, wg_interface, download_speed, upload_speed):
                        logger.debug(f"Full limited VPN client created successfully for {client_name}")
                        return True
                    else:
                        logger.debug(f"Failed to apply bandwidth limits for {client_name}")
                        return False
                else:
                    logger.debug(f"Failed to schedule VPN client {client_name}")
                    return False
            else:
                logger.debug(f"Failed to create VPN client {client_name}")
                return False

        # Create a time-limited VPN client (no bandwidth limitations)
        if not download_speed and not upload_speed:
            wg_interface = "wg0"
            vpn_type = "time_limited"
            if create_vpn_client(client_name, wg_interface, vpn_status, vpn_type):
                if vpn_set_temporary_client_schedulers.set_vpn_client_scheduler(client_name, start_time, end_time, auto_deletion):
                    logger.debug(f"Time-limited VPN client created successfully for {client_name}")
                    return True
                else:
                    logger.debug(f"Failed to schedule VPN client {client_name}")
                    return False
            else:
                logger.debug(f"Failed to create VPN client {client_name}")
                return False

    finally:
        # Always deactivate the VPN client regardless of the result
        disable_vpn_client(client_name)
        logger.info(f"VPN client {client_name} has been deactivated.")
