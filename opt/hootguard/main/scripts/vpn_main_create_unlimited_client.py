# Script Name: vpn_create_unlimited_client_main.py
# Version: 0.7
# Author: HootGuard
# Date: 4. October 2024

# Description:
# This script orchestrates the creation of a new WireGuard VPN client. It generates the client's private, public, 
# and preshared keys, assigns unique IP addresses, retrieves DNS settings, and generates the client configuration 
# file. It then appends the client's peer configuration to the appropriate WireGuard interface configuration 
# file (wg0 or wg1) and reloads the WireGuard interface to apply the changes.

from .vpn import vpn_generate_client_keys
from .vpn import vpn_create_client_ip_addresses_and_store_in_db
from .vpn import vpn_get_primary_dns
from .vpn import vpn_create_client_config
from .vpn import vpn_get_public_server_key
from .vpn import vpn_append_peer_to_wg_config
from .vpn import vpn_reload_wireguard_config
from .vpn import vpn_get_vpn_endpoint_and_secondary_dns_from_global_config
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_ENDPOINT = config['vpn']['endpoint']
VPN_SECONDARY_DNS = config['network']['secondary_dns']

def create_vpn_client(client_name, interface, vpn_status, vpn_type):
    """Main function to create a VPN client, gather keys, IPs, DNS, and store configs."""
    
    # Step 1: Generate client keys
    logger.debug("Generating client keys...")
    client_priv_key, client_pub_key, client_psk = vpn_generate_client_keys.generate_keys(client_name)
    if not client_priv_key or not client_pub_key or not client_psk:
        logger.debug(f"Failed to generate keys for {client_name}")
        return False

    # Step 2: Generate IP addresses and store in DB
    logger.debug("Generating IP addresses...")
    ipv4_address, ipv6_address = vpn_create_client_ip_addresses_and_store_in_db.generate_and_store_ip(interface, client_name, vpn_status, vpn_type)
    if not ipv4_address or not ipv6_address:
        logger.debug(f"Failed to generate IP addresses for {client_name}")
        return False

    # Step 3: Get primary DNS (from NETWORK_INTERFACE_1)
    logger.debug("Getting primary DNS...")
    primary_dns = vpn_get_primary_dns.get_primary_dns()
    if not primary_dns:
        logger.debug(f"Failed to get primary DNS for {client_name}")
        return False

    # Step 4: Get secondary DNS and VPN endpoint
    logger.debug("Getting secondary DNS and VPN endpoint...")
    print (f"VPN ENDPOINT = {VPN_ENDPOINT}")
    endpoint, secondary_dns = vpn_get_vpn_endpoint_and_secondary_dns_from_global_config.get_endpoint_and_secondary_dns()
    #secondary_dns = VPN_SECONDARY_DNS
    #endpoint = VPN_ENDPOINT

    # Step 5: Get the server's public key
    logger.debug(f"Getting server public key for {interface}...")
    server_pub_key = vpn_get_public_server_key.get_public_server_key(interface)
    if not server_pub_key:
        logger.debug(f"Failed to get server public key for {interface}")
        return False

    # Step 6: Determine the port based on the WireGuard interface
    if interface == "wg0":
        port = 51820
    elif interface == "wg1":
        port = 51821
    else:
        logger.debug(f"Invalid WireGuard interface: {interface}")
        port = None

    # Step 7: Create the client configuration file
    logger.debug("Creating client configuration file...")
    success = vpn_create_client_config.create_client_config(
        client_name, client_priv_key, ipv4_address, ipv6_address,
        primary_dns, secondary_dns, server_pub_key, client_psk, endpoint, port
    )
    if not success:
        logger.debug(f"Failed to create VPN client configuration for {client_name}.")
        return False

    # Step 8: Append the peer configuration to the WireGuard interface config file
    logger.debug(f"Appending peer configuration for {client_name} to {interface} config file...")
    peer_append_success = vpn_append_peer_to_wg_config.append_peer_to_wg_config(
        client_name, client_pub_key, client_psk, ipv4_address, ipv6_address, interface
    )
    if not peer_append_success:
        logger.debug(f"Failed to append peer configuration for {client_name} to {interface} config file.")
        return False

    # Step 9: Reload the WireGuard server config to apply the changes
    logger.debug(f"Reloading WireGuard configuration for interface: {interface}...")
    if not vpn_reload_wireguard_config.vpn_reload_wg_interface(interface):
        logger.debug(f"Failed to reload WireGuard configuration for {interface}.")
        return False
    logger.debug(f"WireGuard configuration for {interface} reloaded successfully.")

    logger.info(f"VPN client {client_name} created successfully and peer configuration added.")
    return True
