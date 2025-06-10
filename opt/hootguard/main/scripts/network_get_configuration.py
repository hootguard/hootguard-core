# Script Name: network_get_configuration.py
# Version: 0.8
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script retrieves network configuration information from the `/etc/dhcpcd.conf` file for the 'eth0' interface.
# It determines whether the configuration is static or DHCP for both IPv4 and IPv6. The script also retrieves the 
# standard gateway information and converts subnet prefix lengths into subnet masks. It outputs the active network 
# configuration, including IP addresses, subnet masks, and gateway details.

import subprocess
import ipaddress
#from .global_config import NW_DHCPCD_PATH
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
NW_DHCPCD_PATH = config['dhcp']['dhcpcd_path']

def get_ip_address(interface):
    """Retrieve the IPv4 and IPv6 addresses for the given interface."""
    logger.debug(f"INFO - Retrieving IP addresses for interface {interface}")
    try:
        result = subprocess.run(['ip', 'addr', 'show', interface], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            ipv4_address = "Not set"
            ipv4_subnet_prefix = "Not set"
            ipv6_address = "Not set"
            for line in result.stdout.split('\n'):
                if 'inet ' in line and 'scope global' in line:
                    ipv4_address = line.split()[1].split('/')[0]
                    ipv4_subnet_prefix = line.split()[1].split('/')[1]  # Get the subnet mask prefix
                if 'inet6 ' in line and 'scope global' in line:
                    ipv6_address = line.split()[1].split('/')[0]
            logger.debug(f"INFO - Retrieved IPv4: {ipv4_address}, IPv6: {ipv6_address}")
            return ipv4_address, ipv4_subnet_prefix, ipv6_address
        logger.debug("ERROR - Failed to retrieve IP addresses.")
        return "Not set", "Not set", "Not set"
    except Exception as e:
        logger.error(f"ERROR - Error retrieving IP address for {interface}: {str(e)}")
        return "Not set", "Not set", "Not set"

def get_default_gateway():
    """Retrieve the default IPv4 gateway."""
    logger.debug("INFO - Retrieving default IPv4 gateway")
    try:
        result = subprocess.run(['ip', 'route', 'show', 'default'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('default via'):
                    return line.split()[2]
        logger.debug("ERROR - No default gateway found.")
        return "Not set"
    except Exception as e:
        logger.error(f"ERROR - Error retrieving default gateway: {str(e)}")
        return "Not set"

def prefix_to_subnet_mask(prefix):
    """Convert a subnet prefix length to a subnet mask."""
    logger.debug(f"INFO - Converting prefix {prefix} to subnet mask")
    try:
        # Convert the prefix length to an integer
        prefix = int(prefix)
        # Convert the prefix length to a subnet mask
        return str(ipaddress.IPv4Network(f'0.0.0.0/{prefix}').netmask)
    except Exception as e:
        logger.error(f"ERROR - Error converting prefix to subnet mask: {str(e)}")
        return "Not set"

#def get_default_gateway_v6():
#    try:
#        result = subprocess.run(['ip', '-6', 'route', 'show', 'default'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#        if result.returncode == 0:
#            for line in result.stdout.split('\n'):
#                if line.startswith('default via'):
#                    return line.split()[2]
#        return "Not set"
#    except Exception as e:
#        print(f"Error retrieving default IPv6 gateway: {e    """Retrieve the default IPv4 gateway."""
#    logger.debug("INFO - Retrieving default IPv4 gateway")}")
#        return "Not set"

def network_get_active_config():
    """Retrieve the active network configuration."""
    logger.debug(f"INFO - Retrieving active network configuration from {NW_DHCPCD_PATH}")
    config = {
        "ip_address": "Not set",
        "subnet_mask": "Not set",
        "standard_gw": "Not set",
        "ipv6_address": "Not set",
#        "standard_gwv6": "Not set",
        "type": "DHCP",
        "typev6": "DHCP"
    }  # Default values
    try:
        with open(NW_DHCPCD_PATH, 'r') as file:
            eth0_config = False
            for line in file:
                if line.startswith("interface eth0"):
                    eth0_config = True
                if eth0_config and "static ip_address" in line:
                    if line.strip().startswith("#"):
                        # Line is commented out, hence DHCP is active
                        config["type"] = "DHCP"
                    else:
                        # Static IP configuration is active
                        config["ip_address"] = line.split("=")[1].strip()
                        config["subnet_mask"] = prefix_to_subnet_mask(line.split("=")[1].strip().split("/")[1])
                        config["type"] = "Static"
                elif eth0_config and "static ip6_address" in line:
                    if line.strip().startswith("#"):
                        # Line is commented out, hence DHCP is active
                        config["typev6"] = "DHCP"
                    else:
                        # Static IPv6 configuration is active
                        # config["ipv6_address"] = line.split("=")[1].strip()
                        ipv6_full_address = line.split("=")[1].strip()
                        config["ipv6_address"] = ipv6_full_address.split("/")[0]  # Remove the subnet prefix
                        config["typev6"] = "Static"
                elif eth0_config and line.strip() == "":
                    break  # End of eth0 config block
            if config["type"] == "DHCP" or config["typev6"] == "DHCP":
                ipv4_address, ipv4_subnet_prefix, ipv6_address = get_ip_address("eth0")
                if config["type"] == "DHCP":
                    config["ip_address"] = ipv4_address
                    config["subnet_mask"] = prefix_to_subnet_mask(ipv4_subnet_prefix)
                if config["typev6"] == "DHCP":
                    # config["ipv6_address"] = ipv6_address
                    config["ipv6_address"] = ipv6_address.split("/")[0]  # Remove the subnet prefix
            config["standard_gw"] = get_default_gateway()
        logger.debug(f"INFO - Active network configuration: {config}")
        return config
    except Exception as e:
        logger.error(f"ERROR - Error reading {NW_DHCPCD_PATH}: {str(e)}")
        return config
