# Script Name: ddns_configure_user_dynu.py
# Version: 0.2
# Author: HootGuard
# Date: 27. January 2025

# Description:
# This script updates the DYNU Bash script file (either 'user-dynu.sh' for IPv4 or the IPv6 equivalent) 
# with new key information. It facilitates dynamic modification of the key
# used for DYNU updates, based on the IP version provided (IPv4 or IPv6).

import re
import subprocess
from .ddns_update_endpoint_in_global_config import replace_vpn_endpoint
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_DYNU_SCRIPT_PATH = config['ddns']['user_dynu_script']
DDNS_USER_DYNU_V6_SCRIPT_PATH = config['ddns']['user_dynu_v6_script']

def ddns_write_and_activate_dynu(domain, password, ip_version, initial_setup=None):
    # Update the respective Dynu script file (IPv4 or IPv6) with the new domain and password.
    
    # Determine the file path based on the IP version
    if ip_version == "ipv4":
        script_path = DDNS_USER_DYNU_SCRIPT_PATH
    elif ip_version == "ipv6":
        script_path = DDNS_USER_DYNU_V6_SCRIPT_PATH
    else:
        logger.debug("ERROR - Invalid IP version. Please specify 'ipv4' or 'ipv6'.")
        return False
    
    try:
        # Open the existing DYNU script
        with open(script_path, 'r') as file:
            content = file.read()

        # Replace the KEY= line with the new key using regex
        updated_content = re.sub(r'^PW=.*$', f'PW="{password}"', content, flags=re.MULTILINE)
        updated_content = re.sub(r'^HN=.*$', f'HN="{domain}"', updated_content, flags=re.MULTILINE)

        # Write the updated content back to the file
        with open(script_path, 'w') as file:
            file.write(updated_content)
        logger.debug(f"SUCCESS - DYNU {ip_version} script updated successfully.")

        # Only run the following lines if this is not part of the initial_setup procedure
        if not initial_setup:
            # Update the endpoint in the global_config.yaml file to the new record_name
            if replace_vpn_endpoint(domain):
                logger.debug("SUCCESS - VPN endpoint updated successfully in global_config.yaml.")
            else:
                logger.debug("ERROR - Failed to update endpoint in global_config.yaml.")

            # Execute the updated DYNU script
            subprocess.run(['/bin/bash', script_path], check=True)
            logger.debug(f"SUCCESS - DYNU {ip_version} script executed successfully.")

        return True
    except Exception as e:
        logger.debug(f"ERROR - An error occurred while updating the DYNU {ip_version} script: {e}")
        return False
