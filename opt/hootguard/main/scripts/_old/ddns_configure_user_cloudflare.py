# Script Name: ddns_configure_user_cloudflare.py
# Version: 1.4
# Author: HootGuard
# Date: 10. September 2024

# Description:
# This script updates the Cloudflare Dynamic DNS (DDNS) Bash script files with new configuration details. It allows users 
# to modify authentication credentials, zone identifier, and DNS record name dynamically.
# It allows updating either IPv4 (A-Record), IPv6 (AAAA-Record), or both based on user choice.

import subprocess
from .ddns_update_endpoint_in_global_config import replace_vpn_endpoint
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_CLOUDFLARE_SCRIPT_PATH = config['ddns']['user_cloudflare_script']
DDNS_USER_CLOUDFLARE_V6_SCRIPT_PATH = config['ddns']['user_cloudflare_v6_script']

def ddns_write_and_activate_cloudflare(auth_email, auth_key, zone_identifier, record_name, ip_version, initial_setup=None):
    def update_script(script_path):
        logger.debug("Update cloudflare ddns has been started")
        try:
            # Read the existing script content
            with open(script_path, 'r') as file:
                content = file.readlines()

            # Update the script lines with new values
            new_content = []
            for line in content:
                if line.startswith('auth_email='):
                    new_content.append(f'auth_email="{auth_email}"\n')
                elif line.startswith('auth_key='):
                    new_content.append(f'auth_key="{auth_key}"\n')
                elif line.startswith('zone_identifier='):
                    new_content.append(f'zone_identifier="{zone_identifier}"\n')
                elif line.startswith('record_name='):
                    new_content.append(f'record_name="{record_name}"\n')
                elif line.startswith('auth_method='):
                    new_content.append('auth_method="global"\n')  # Set auth_method to always "global"
                else:
                    new_content.append(line)
            # Write the updated content back to the file
            with open(script_path, 'w') as file:
                file.writelines(new_content)
            logger.debug(f"SUCESS - Cloudflare DDNS script {script_path} updated successfully.")

            # Only run the following lines if this is not part of the initial_setup procedure
            if not initial_setup:
   	        # Update the endpoint in the global_config.yaml file to the new record_name
                if replace_vpn_endpoint(record_name):
                    logger.debug("INFO - VPN endpoint updated successfully in global config.")
                else:
                    logger.debug("ERROR - Failed to update VPN endpoint in global config.")

                # Execute the updated Cloudflare script
                subprocess.run(['/bin/bash', script_path], check=True)
                logger.debug(f"SUCCESS - Cloudflare {ip_version} script executed successfully.")

            return True
        except Exception as e:
            logger.debug(f"ERROR - An error occurred while updating the Cloudflare DDNS script {script_path}: {e}")
            return False

    # Determine which scripts to update based on the IP version
    if ip_version == "ipv4":
        return update_script(DDNS_USER_CLOUDFLARE_SCRIPT_PATH)
    elif ip_version == "ipv6":
        return update_script(DDNS_USER_CLOUDFLARE_V6_SCRIPT_PATH)
    else:
        logger.debug("ERROR - Invalid IP version specified. Please choose 'ipv4' or 'ipv6'.")
        return False
