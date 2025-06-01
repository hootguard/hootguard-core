# Script Name: vpn_create_client_ip_addresses_and_store_in_db.py
# Version: 0.3
# Author: HootGuard
# Date: 30. September 2024

# Description:
# This script dynamically generates unique IPv4 and IPv6 addresses for WireGuard VPN clients
# based on the interface (wg0 or wg1). The script retrieves base IP addresses from the interfaces,
# ensures the new IP addresses are not already in use, and stores the client details along with
# the generated IP addresses in a SQLite database.

# The script includes the following key functions:
# 1. `get_interface_ips(interface)`: Retrieves the base IPv4 and IPv6 addresses from the WireGuard interface.
# 2. `get_used_ips(interface)`: Retrieves all the currently used IP addresses for the given interface from the database.
# 3. `generate_unique_ip(interface)`: Generates unique IPv4 and IPv6 addresses by incrementing the last part of the base addresses.
# 4. `store_client_in_db(client_name, ipv4_address, ipv6_address, interface)`: Stores the client details and their assigned IP addresses in the SQLite database.

# Example usage:
# The script generates and stores the client IPs for the "wg1" interface, with "test_client" as the client name.

import sqlite3
import subprocess
#from scripts.global_config import VPN_CLIENTS_DB_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_CLIENTS_DB_PATH = config['vpn']['client_db_path']

def get_interface_ips(interface):
    """Retrieve the base IPv4 and IPv6 addresses from the WireGuard interface."""
    ipv4_base = None
    ipv6_base = None
    try:
        # Run the ip command to get the interface IP addresses
        result = subprocess.check_output(['ip', 'addr', 'show', interface]).decode('utf-8')

        # Find the IPv4 and IPv6 addresses
        ipv4_address = None
        ipv6_address = None
        for line in result.splitlines():
            line = line.strip()
            if "inet " in line:  # IPv4 address
                ipv4_address = line.split()[1].split('/')[0]
            elif "inet6 " in line:  # IPv6 address
                ipv6_address = line.split()[1].split('/')[0]

        # Extract the base part of the IPs
        if ipv4_address:
            ipv4_base = '.'.join(ipv4_address.split('.')[:-1]) + '.'
        if ipv6_address:
            ipv6_base = ':'.join(ipv6_address.split(':')[:-1]) + ':'

        logger.debug(f"Retrieved IPs for interface {interface}: IPv4 base: {ipv4_base}, IPv6 base: {ipv6_base}")
        return ipv4_base, ipv6_base
    except subprocess.CalledProcessError as e:
        logger.debug(f"Failed to retrieve IPs for interface {interface}: {str(e)}")
        return None, None

def get_used_ips(interface):
    """Retrieve all IP addresses currently in use for the given interface."""
    try:
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT ipv4_address, ipv6_address FROM all_vpn_clients WHERE wg_interface = ?;
        """, (interface,))
        used_ips = cursor.fetchall()  # List of (ipv4_address, ipv6_address) tuples
        conn.close()
        logger.debug(f"Retrieved used IPs for interface {interface}.")
        return used_ips
    except Exception as e:
        logger.debug(f"Failed to retrieve used IPs for interface {interface}: {str(e)}")
        return []

def generate_unique_ip(interface):
    """Generate a unique IPv4 and IPv6 address based on the WireGuard interface."""
    try:
        # Dynamically retrieve base IP address ranges for wg0 and wg1
        ipv4_base, ipv6_base = get_interface_ips(interface)
        if not ipv4_base and not ipv6_base:
            logger.debug("Failed to retrieve base IP addresses.")
            return None, None

        # Get currently used IP addresses for this interface
        used_ips = get_used_ips(interface)
        used_ipv4 = {ip[0] for ip in used_ips}
        used_ipv6 = {ip[1] for ip in used_ips}

        # Generate new IP addresses (start with 2, to avoid .1 typically being the server)
        for i in range(2, 255):
            ipv4_address = f"{ipv4_base}{i}" if ipv4_base else None
            ipv6_address = f"{ipv6_base}{i:03x}/64" if ipv6_base else None

            # Ensure the generated IPs are not already in use
            if (ipv4_address not in used_ipv4) and (ipv6_address not in used_ipv6):
                logger.debug(f"Generated unique IPs for interface {interface}: IPv4: {ipv4_address}, IPv6: {ipv6_address}")
                return ipv4_address, ipv6_address

        logger.debug(f"No available IP addresses in the range for interface {interface}.")
        return None, None
    except Exception as e:
        logger.debug(f"Failed to generate unique IP for interface {interface}: {str(e)}")
        return None, None

def store_client_in_db(client_name, ipv4_address, ipv6_address, interface, vpn_status, vpn_type):
    """Store the client details in the SQLite database."""
    try:
        conn = sqlite3.connect(VPN_CLIENTS_DB_PATH)
        cursor = conn.cursor()

        # Insert the client details into the database
        cursor.execute("""
        INSERT INTO all_vpn_clients (client_name, ipv4_address, ipv6_address, wg_interface, vpn_status, vpn_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (client_name, ipv4_address, ipv6_address, interface, vpn_status, vpn_type))

        conn.commit()
        conn.close()
        logger.debug(f"Stored client {client_name} in the database with IPv4: {ipv4_address}, IPv6: {ipv6_address}.")
        return True
    except Exception as e:
        logger.debug(f"Failed to store client {client_name} in the database: {str(e)}")
        return False

def generate_and_store_ip(wg_interface, client_name, vpn_status, vpn_type):
    """Generate unique IP addresses and store them in the database, returning the IPs."""
    ipv4_address, ipv6_address = generate_unique_ip(wg_interface)
    if ipv4_address and ipv6_address:
        success = store_client_in_db(client_name, ipv4_address, ipv6_address, wg_interface, vpn_status, vpn_type)
        if success:
            return ipv4_address, ipv6_address
    return None, None
