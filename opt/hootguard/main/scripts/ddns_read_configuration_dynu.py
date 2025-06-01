# Script Name: ddns_read_configuration_dynu.py
# Version: 0.2
# Author: HootGuard
# Date: 24. January 2025

# Description:
# This script reads the configuration from two DYNU scripts (for IPv4 and IPv6) in the HootGuard system.
# It extracts the key from each script.
# The extracted values are returned for further processing.
# HN = Hostname but in this script represented by the "domain"
# PW = Password but in this script represented by the "key"

import re
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_DYNU_SCRIPT_PATH = config['ddns']['user_dynu_script']
DDNS_USER_DYNU_V6_SCRIPT_PATH = config['ddns']['user_dynu_v6_script']

def ddns_read_config_dynu():
    """Read the Dynu DDNS configuration for both IPv4 and IPv6."""

    def extract_password_and_domain(file_path):
        logger.debug(f"INFO - Extracting key and domain from {file_path}")
        try:
            with open(file_path, 'r') as file:
                content = file.read()

            # Regular expressions to find the KEY and DOMAIN values
            password_pattern = r'^PW="([^"]+)"'
            domain_pattern = r'^HN="([^"]+)"'

            password_match = re.search(password_pattern, content, re.MULTILINE)
            domain_match = re.search(domain_pattern, content, re.MULTILINE)

            password = password_match.group(1) if password_match else None
            domain = domain_match.group(1) if domain_match else None

            if password:
                logger.debug(f"INFO - Extracted Password from {file_path}")
            else:
                logger.debug(f"ERROR - No Password found in {file_path}")

            if domain:
                logger.debug(f"INFO - Extracted DOMAIN from {file_path}")
            else:
                logger.debug(f"ERROR - No DOMAIN found in {file_path}")

            return domain, password
        except FileNotFoundError as e:
            logger.debug(f"ERROR - Configuration file not found: {str(e)}")
            return None, None
        except Exception as e:
            logger.debug(f"ERROR - Unexpected error reading {file_path}: {str(e)}")
            return None, None

    # Read configuration from both IPv4 and IPv6 script files
    logger.debug(f"INFO - Reading IPv4 configuration from {DDNS_USER_DYNU_SCRIPT_PATH} and {DDNS_USER_DYNU_V6_SCRIPT_PATH}")
    ipv4_domain, ipv4_key = extract_password_and_domain(DDNS_USER_DYNU_SCRIPT_PATH)
    ipv6_domain, ipv6_key = extract_password_and_domain(DDNS_USER_DYNU_V6_SCRIPT_PATH)

    return ipv4_domain, ipv4_key, ipv6_domain, ipv6_key
