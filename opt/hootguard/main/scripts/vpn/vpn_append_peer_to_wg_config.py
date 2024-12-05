# Script Name: vpn_append_peer_to_wg_config.py
# Version: 0.7
# Author: HootGuard
# Date: 3. October 2024

# Description:
# This script appends a new peer (client) configuration to the WireGuard configuration file for a specified interface
# (wg0 or wg1). The configuration includes the client's public key, pre-shared key, and the allocated IPv4 and IPv6 
# addresses. The IPv6 address is automatically stripped of its prefix before being appended.

import subprocess
#from scripts.global_config import VPN_WIREGUARD_PATH
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
VPN_WIREGUARD_PATH = config['vpn']['wireguard_main_path']

def append_peer_to_wg_config(client_name, client_pub_key, client_psk, ipv4_address, ipv6_address, interface):
    """Append the peer configuration to the WireGuard config (wg0.conf or wg1.conf)"""

    # Define the WireGuard config file based on the interface
    config_file = f"{VPN_WIREGUARD_PATH}/{interface}.conf"
    
    #Remove the IPv6 prefix before appending the peer configuration
    ipv6_address_without_prefix = ipv6_address.split('/')[0]  # Remove the /64 prefix

    # Peer configuration content to be added (no leading or trailing newlines)
    peer_config = (
        f"### begin {client_name} ###\n"
        f"[Peer]\n"
        f"PublicKey = {client_pub_key}\n"
        f"PresharedKey = {client_psk}\n"
        f"AllowedIPs = {ipv4_address}/32,{ipv6_address_without_prefix}/128\n"
        f"### end {client_name} ###"
    )

    try:
        # Delegate the append operation to the centralized /usr/local/bin/hootguard script
        result = subprocess.run(
            [
                '/usr/bin/sudo', '/usr/local/bin/hootguard', 'append-peer',
                interface, peer_config
            ],
            capture_output=True, text=True, check=True
        )
        logger.debug(f"Peer configuration for {client_name} added to {config_file}. Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.debug(f"Failed to append peer configuration for {client_name} to {config_file}: {e.stderr}")
        return False
