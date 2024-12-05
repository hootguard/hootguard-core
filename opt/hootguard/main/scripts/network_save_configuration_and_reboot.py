# Script Name: network_save_configuration_and_reboot.py
# Version: 1.5
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script modifies and saves the network configuration for the 'eth0' interface, handling both IPv4 and IPv6 settings.
# It first checks if existing configurations are present and then replaces them with new settings, writing the changes 
# to the '/etc/dhcpcd.conf' file. The script also supports calculating subnet masks, backing up and restoring configurations, 
# and automatically reboots the system after saving changes to apply the new network settings.

import subprocess
import shutil
import os
import ipaddress
from .network_update_ip_address_in_global_config import replace_network_ip_address
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
NW_DHCPCD_PATH = config['dhcp']['dhcpcd_path']
NW_DHCPCD_BACKUP_PATH = config['dhcp']['dhcpcd_backup_path']

# Check whether an active IPv4 configuration exists already in the /etc/dhcpcd.conf file and if an active IPv4 config
# already exists, copy it to restore it in the new file.
def network_check_if_ipv4_already_exists():
    """Check if IPv4 configuration exists for eth0."""
    logger.debug("INFO - Checking if IPv4 configuration already exists.")
    try:
        with open(NW_DHCPCD_PATH, 'r') as file:
            lines = file.readlines()
        ipv4_config = ""
        in_ipv4_block = False
        for line in lines:
            if line.startswith("interface eth0"):
                in_ipv4_block = True
            elif in_ipv4_block:
                if line.startswith("static ip_address") or line.startswith("static routers") or line.startswith("static domain_name_servers"):
                    ipv4_config += line
                elif line.startswith("interface"):
                    in_ipv4_block = False
            if not in_ipv4_block and ipv4_config:
                break
        return ipv4_config.strip()
    except Exception as e:
        logger.debug(f"ERROR - Network - Error checking existing IPv4 configuration: {e}")
        return ""



# Check whether an active IPv6 configuration exists already in the /etc/dhcpcd.conf file and if an active IPv6 config
# already exists, copy it to restore it in the new file.
def network_check_if_ipv6_already_exists():
    """Check if IPv6 configuration exists for eth0."""
    logger.debug("INFO - Checking if IPv6 configuration already exists.")
    ipv6_key = "static ip6_address="

    try:
        with open(NW_DHCPCD_PATH, 'r') as file:
            for line in file:
                if ipv6_key in line:  # Directly check if the key is in the line
                    stripped_line = line.strip()
                    if stripped_line.startswith(ipv6_key):
                        logger.debug(f"INFO - Network - IPv6 address discovered and handed over")
                        return stripped_line
        return ""
    except Exception as e:
        logger.debug(f"ERROR - Network - Error checking existing IPv6 configuration: {e}")
        return ""



# --- CHANGE IPv4 SETTING ---
def network_save_config_and_reboot(ip_address, subnet_mask, standard_gateway, initial_setup=None):
    """Save new IPv4 configuration and reboot the system."""
    logger.debug(f"INFO - Saving IPv4 configuration: {ip_address}, {subnet_mask}, {standard_gateway}")

    # Check for existing IPv6 configuration
    ipv6_config = network_check_if_ipv6_already_exists()

    # Restore backup using hootguard
    subprocess.run(['/usr/bin/sudo', '/usr/local/bin/hootguard', 'restore-backup', NW_DHCPCD_BACKUP_PATH, NW_DHCPCD_PATH], check=True)

    # Convert subnet mask to CIDR notation
    cidr = subnet_mask_to_cidr(subnet_mask)

    # Prepare the configuration string for static IP
    static_config = f"""
# Static ip configuration
interface eth0
static ip_address={ip_address}/{cidr}
static routers={standard_gateway}
static domain_name_servers={ip_address}
{ipv6_config}
"""
    # Write the new configuration to a temporary file
    with open('/tmp/dhcpcd_temp.conf', 'w') as file:
        file.write(static_config)

    # Update network configuration using hootguard
    subprocess.run(['/usr/bin/sudo', '/usr/local/bin/hootguard', 'update-network-config', '/tmp/dhcpcd_temp.conf', NW_DHCPCD_PATH], check=True)

    # Replace ip address and the primary dns in global_config.yaml file
    ipv4_address = f"{ip_address}/{cidr}"
    if not replace_network_ip_address("ipv4", ipv4_address, ip_address):
        logger.debug(f"ERROR - Network - Error updating ip v4 address and/or primary dns in global config")

    if not initial_setup:
        # Reboot the system after successful ip settings update
        reboot_system()
    else:
        logger.info("INFO - Initial setup detected. Skipping system reboot for ip settings.")
        return True  # Ip settings successfully updated, for initial setup main script



# --- CHANGE IPv6 SETTING ---
def network_save_config_and_reboot_v6(ip_address_v6):
    """Save new IPv6 configuration and reboot the system."""
    logger.debug(f"INFO - Saving IPv6 configuration: {ip_address_v6}")

    # Check for existing IPv4 configuration
    ipv4_config = network_check_if_ipv4_already_exists()

    # Restore backup using hootguard
    subprocess.run(['/usr/bin/sudo', '/usr/local/bin/hootguard', 'restore-backup', NW_DHCPCD_BACKUP_PATH, NW_DHCPCD_PATH], check=True)
    
    # Calculate ipv6 subnet prefix
    ipv6_prefix = calculate_ipv6_subnet_prefix(ip_address_v6)
    #print("PREFIX:", ipv6_prefix)

    # Prepare the configuration string for static IPv6
    static_config_v6 = f"""
# Static IPv6 configuration
interface eth0
static ip6_address={ip_address_v6}/{ipv6_prefix}
{ipv4_config}
"""
    # Write the new configuration to a temporary file
    with open('/tmp/dhcpcd_temp_v6.conf', 'w') as file:
        file.write(static_config_v6)

    # Update network configuration using hootguard
    subprocess.run(['/usr/bin/sudo', '/usr/local/bin/hootguard', 'update-network-config', '/tmp/dhcpcd_temp_v6.conf', NW_DHCPCD_PATH], check=True)

    # Replace ip address in global_config.yaml file
    ipv6_address = f"{ip_address_v6}/{ipv6_prefix}"
    if not replace_network_ip_address("ipv6", ipv6_address):
        logger.debug(f"ERROR - Network - Error updating ip v6 address in global config")

    # Call reboot_system() function after all other operations
    reboot_system()



# Function to convert a traditional subnet mask to CIDR notation (e.g. /24)
def subnet_mask_to_cidr(subnet_mask):
    """Convert subnet mask to CIDR notation."""
    return sum([bin(int(x)).count('1') for x in subnet_mask.split('.')])



# Function to extract ipv6 subnet prefix for dhcpcd.conf entry
def calculate_ipv6_subnet_prefix(ipv6_address):
    """Calculate the subnet prefix for an IPv6 address."""    
    try:
        # Create an IPv6 address object
        ip = ipaddress.IPv6Address(ipv6_address)

        # Print the IPv6 address and its prefix length
        logger.debug(f"INFO - Calculating IPv6 prefix for {ipv6_address}")

        # Describes the first 64 bits are the network portion
        subnet_prefix_length = 64  # Default for most IPv6 addresses

        return subnet_prefix_length
    except ipaddress.AddressValueError as e:
        logger.debug(f"ERROR - Invalid IPv6 address: {e}")
        return None


# Reboot the system to apply network changes
def reboot_system():
    """1. Restart the firewall with the new parameters (ip-address)"""
    # Activate production firewall and restart the netfilter to activate the rules
    logger.info("Network - Rebooting the system")
    try:
        # Restart the firewall
        logger.info("Restarting firewall with updated iptables settings.")
        subprocess.run(
            ['/usr/bin/sudo', '/usr/local/bin/hootguard', 'restart-firewall', config['vpn']['iptables_settings_file']],
            check=True
        )
        logger.info("Firewall restarted successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"ERROR - Failed to restart the firewall: {e}")
        # return False
        error_occurred = True

    """2. Reboot the system to apply the new network configuration."""
    logger.info("Network - Rebooting the system")
    try:
        logger.info("Network - Rebooting the system")
        # Execute the reboot command
        subprocess.run(['sudo', 'reboot'], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"ERROR - Error during reboot: {e}")

    try:
        # Reboot the system
        logger.info("Rebooting the system.")
        subprocess.run(['/usr/bin/sudo', '/usr/local/bin/hootguard', 'reboot-system'], check=True)
        logger.info("System rebooted successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"ERROR - Failed to reboot the system: {e}")
        #return False
        error_occurred = True

    #return True
    error_occurred = False
