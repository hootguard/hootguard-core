# Script Name: ddns_read_configuration_ipv64.py
# Version: 0.2
# Author: HootGuard
# Date: 24. January 2025

# Description:
# This script reads the configuration from two IPv64 scripts (for IPv4 and IPv6) in the HootGuard system.
# It extracts the key from each script.
# The extracted values are returned for further processing.

import re
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_IPV64_SCRIPT_PATH = config['ddns']['user_ipv64_script']
DDNS_USER_IPV64_V6_SCRIPT_PATH = config['ddns']['user_ipv64_v6_script']

def ddns_read_config_ipv64():
    """Read the IPv64 DDNS configuration for both IPv4 and IPv6."""

    def extract_key_and_domain(file_path):
        logger.debug(f"INFO - Extracting key and domain from {file_path}")
        try:
            with open(file_path, 'r') as file:
                content = file.read()

            # Regular expressions to find the KEY and DOMAIN values
            key_pattern = r'^KEY="([^"]+)"'
            domain_pattern = r'^DOMAIN="([^"]+)"'

            key_match = re.search(key_pattern, content, re.MULTILINE)
            domain_match = re.search(domain_pattern, content, re.MULTILINE)

            key = key_match.group(1) if key_match else None
            domain = domain_match.group(1) if domain_match else None

            if key:
                logger.debug(f"INFO - Extracted KEY: {key} from {file_path}")
            else:
                logger.debug(f"ERROR - No KEY found in {file_path}")

            if domain:
                logger.debug(f"INFO - Extracted DOMAIN: {domain} from {file_path}")
            else:
                logger.debug(f"ERROR - No DOMAIN found in {file_path}")

            return domain, key
        except FileNotFoundError as e:
            logger.debug(f"ERROR - Configuration file not found: {str(e)}")
            return None, None
        except Exception as e:
            logger.debug(f"ERROR - Unexpected error reading {file_path}: {str(e)}")
            return None, None

    # Read configuration from both IPv4 and IPv6 script files
    logger.debug(f"INFO - Reading IPv4 configuration from {DDNS_USER_IPV64_SCRIPT_PATH} and {DDNS_USER_IPV64_V6_SCRIPT_PATH}")
    ipv4_domain, ipv4_key = extract_key_and_domain(DDNS_USER_IPV64_SCRIPT_PATH)
    ipv6_domain, ipv6_key = extract_key_and_domain(DDNS_USER_IPV64_V6_SCRIPT_PATH)

    return ipv4_domain, ipv4_key, ipv6_domain, ipv6_key
