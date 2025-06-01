#!/usr/bin/python3
# Script Name: export_network_config.py
# Version: 0.2
# Author: HootGuard
# Date: 11. January 2025

# Description:
# This script reads the global YAML configuration file and extracts network and VPN settings.
# It calculates IPv4/IPv6 subnets for WireGuard interfaces and outputs settings as Bash export variables.
# Key exports include interface names, IP addresses, subnets, and primary DNS, formatted for shell usage.

import yaml
import os

# Path to your global configuration YAML file
config_file_path = "/opt/hootguard/misc/global_config.yaml"

# Load the YAML file
with open(config_file_path, "r") as file:
    config = yaml.safe_load(file)

# Extract values from the YAML
eth_interface_1 = config['network']['interface_1']
eth_interface_1_network = config['network']['interface_1_v4_network']
wg_interface_1 = config['vpn']['wireguard_interface_1']
wg_interface_2 = config['vpn']['wireguard_interface_2']
ipv4_address_wg_int_1 = config['vpn']['wireguard_interface_1_v4_ip_addresse']
ipv4_address_wg_int_2 = config['vpn']['wireguard_interface_2_v4_ip_addresse']
#ipv6_address_wg_int_1 = config['vpn']['wireguard_interface_1_v6_ip_addresse']
#ipv6_address_wg_int_2 = config['vpn']['wireguard_interface_2_v6_ip_addresse']
primary_dns = config['network']['primary_dns']


# Calculate the subnet for ipv4_network_wg_int_1 and ipv4_network_wg_int_2
ipv4_network_wg_int_1 = ".".join(config['vpn']['wireguard_interface_1_v4_ip_addresse'].split(".")[:-1]) + ".0/24"
ipv4_network_wg_int_2 = ".".join(config['vpn']['wireguard_interface_2_v4_ip_addresse'].split(".")[:-1]) + ".0/24"
ipv6_network_wg_int_1 = config['vpn']['wireguard_interface_1_v6_ip_addresse'].split("::")[0] + "::/64"
ipv6_network_wg_int_2 = config['vpn']['wireguard_interface_2_v6_ip_addresse'].split("::")[0] + "::/64"

# Print variables in bash export format
print(f'export ETH_INTERFACE_1="{eth_interface_1}"')
print(f'export ETH_INTERFACE_1_NETWORK="{eth_interface_1_network}"')
print(f'export WG_INTERFACE_1="{wg_interface_1}"')
print(f'export WG_INTERFACE_2="{wg_interface_2}"')
print(f'export IPV4_ADDRESS_WG_INT_1="{ipv4_address_wg_int_1}"')
print(f'export IPV4_ADDRESS_WG_INT_2="{ipv4_address_wg_int_2}"')
#print(f'export IPV6_ADDRESS_WG_INT_1="{ipv6_address_wg_int_1}"')
#print(f'export IPV6_ADDRESS_WG_INT_2="{ipv6_address_wg_int_2}"')
print(f'export PIHOLE_IP="{primary_dns}"')
print(f'export IPV4_NETWORK_WG_INT_1="{ipv4_network_wg_int_1}"')
print(f'export IPV4_NETWORK_WG_INT_2="{ipv4_network_wg_int_2}"')
print(f'export IPV6_NETWORK_WG_INT_1="{ipv6_network_wg_int_1}"')
print(f'export IPV6_NETWORK_WG_INT_2="{ipv6_network_wg_int_2}"')
