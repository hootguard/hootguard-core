# Script Name: network_free_ipv4.py
# Version: 1.0
# Author: HootGuard
# Date: 23. February 2025

# Description:
# This script identifies a free IPv4 address within the same subnet as the DHCP-assigned IP.
# It retrieves the current network configuration (IP address, subnet mask, and default gateway),
# calculates five potential IP addresses at the upper end of the subnet, and pings them to 
# determine availability. The first unresponsive IP is suggested as a static IP for HootGuard Sentry.

import subprocess
import ipaddress
from .global_logger import logger
from .network_get_configuration import network_get_active_config

def find_free_ip():
    """Find a free IP address in the upper range of the subnet and return it with the subnet mask and gateway."""
    config = network_get_active_config()

    if config["ip_address"] == "Not set" or config["subnet_mask"] == "Not set" or config["standard_gw"] == "Not set":
        logger.error("ERROR - Could not retrieve the current IP configuration.")
        return None, None, None

    try:
        # Convert subnet mask to prefix
        network = ipaddress.IPv4Network(f"{config['ip_address']}/{config['subnet_mask']}", strict=False)
        possible_ips = list(network.hosts())[-10:]  # Get last 10 usable IPs in the subnet

        logger.info(f"INFO - Checking available IPs: {possible_ips}")

        for ip in reversed(possible_ips):  # Start checking from the highest
            if not ping_ip(str(ip)):
                logger.info(f"INFO - Suggested free IP: {ip}")
                return str(ip), config["subnet_mask"], config["standard_gw"]

        logger.warning("WARNING - No free IP found in the suggested range.")
        return None, config["subnet_mask"], config["standard_gw"]
    except Exception as e:
        logger.error(f"ERROR - Exception in finding free IP: {str(e)}")
        return None, None, None

def ping_ip(ip):
    """Ping an IP address to check if it's in use."""
    try:
        result = subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0  # True if IP is in use, False if not
    except Exception as e:
        logger.error(f"ERROR - Exception in pinging {ip}: {str(e)}")
        return True  # Assume IP is in use if an error occurs

if __name__ == "__main__":
    suggested_ip = find_free_ip()
    if suggested_ip:
        print(f"Suggested free IP: {suggested_ip}")
    else:
        print("No free IP found in the suggested range.")
