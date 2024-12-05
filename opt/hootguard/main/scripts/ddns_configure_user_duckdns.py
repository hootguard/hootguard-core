# Script Name: ddns_configure_user_duckdns.py
# Version: 1.5
# Author: HootGuard
# Date: 10. September 2024

# Description:
# This script updates the DuckDNS Bash script file (either 'user-duckdns.sh' for IPv4 or the IPv6 equivalent) 
# with new domain and token information. It facilitates dynamic modification of the domain and token 
# used for DuckDNS updates, based on the IP version provided (IPv4 or IPv6).

import re
import subprocess
from .ddns_update_endpoint_in_global_config import replace_vpn_endpoint
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_DUCKDNS_SCRIPT_PATH = config['ddns']['user_duckdns_script']
DDNS_USER_DUCKDNS_V6_SCRIPT_PATH = config['ddns']['user_duckdns_v6_script']

def ddns_write_and_activate_duckdns(domain, token, ip_version, initial_setup=None):
    """
    Update the respective DuckDNS script file (IPv4 or IPv6) with the new domain and token.
    
    Args:
    - domain (str): The new domain to update DuckDNS with.
    - token (str): The new token to update DuckDNS with.
    - ip_version (str): The IP version ('ipv4' or 'ipv6') to determine which script to update.
    """
    
    # Determine the file path based on the IP version
    if ip_version == "ipv4":
        script_path = DDNS_USER_DUCKDNS_SCRIPT_PATH
    elif ip_version == "ipv6":
        script_path = DDNS_USER_DUCKDNS_V6_SCRIPT_PATH
    else:
        logger.debug("ERROR - Invalid IP version. Please specify 'ipv4' or 'ipv6'.")
        return False
    
    try:
        # Open the existing DuckDNS script
        with open(script_path, 'r') as file:
            content = file.read()

        # Replace the domain and token using regular expressions
        new_content = re.sub(r'domains=[^&]*', f'domains={domain}', content)
        new_content = re.sub(r'token=[^&]*', f'token={token}', new_content)

        # Write the updated content back to the file
        with open(script_path, 'w') as file:
            file.write(new_content)
        logger.debug(f"SUCCESS - DuckDNS {ip_version} script updated successfully.")

        # Only run the following lines if this is not part of the initial_setup procedure
        if not initial_setup:
            # Update the endpoint in the global_config.yaml file to the new record_name
            if replace_vpn_endpoint(domain):
                logger.debug("SUCCESS - VPN endpoint updated successfully in global_config.yaml.")
            else:
                logger.debug("ERROR - Failed to update endpoint in global_config.yaml.")

            # Execute the updated DuckDNS script
            subprocess.run(['/bin/bash', script_path], check=True)
            logger.debug(f"SUCCESS - DuckDNS {ip_version} script executed successfully.")

        return True
    except Exception as e:
        logger.debug(f"ERROR - An error occurred while updating the {ip_version} script: {e}")
        return False
