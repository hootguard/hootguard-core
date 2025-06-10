# Script Name: ddns_read_configuration_duckdns.py
# Version: 0.3
# Author: HootGuard
# Date: 10. September 2024

# Description:
# This script reads the configuration from two DuckDNS scripts (for IPv4 and IPv6) in the HootGuard system.
# It extracts the domain and token from each script based on specific patterns found in URLs.
# The extracted values are returned for further processing. The expected URL format is:
# https://www.duckdns.org/update?domains=<domain>&token=<token>&ip=<ip>
# This version includes logging for improved traceability during execution.

import re
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_DUCKDNS_SCRIPT_PATH = config['ddns']['user_duckdns_script']
DDNS_USER_DUCKDNS_V6_SCRIPT_PATH = config['ddns']['user_duckdns_v6_script']

def ddns_read_config_duckdns():
    """Read the DuckDNS DDNS configuration for both IPv4 and IPv6."""

    # Function to extract domain and token from a given file path
    def extract_domain_token(file_path):
        logger.debug(f"INFO - Extracting domain and token from {file_path}")
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            # Regular expression to extract domains and token
            pattern = r'domains=([\w.-]+)&token=([a-f0-9-]+)'
            match = re.search(pattern, content)
            if match:
                domains = match.group(1)
                token = match.group(2)
                logger.debug(f"INFO - Extracted domain: {domains}, token: {token} from {file_path}")
                return domains, token
            else:
                logger.debug(f"ERROR - No match found for domain and token in {file_path}")
                return None, None
        except FileNotFoundError as e:
            logger.debug(f"ERROR - Configuration file not found: {str(e)}")
            return None, None

    # Read configuration from both IPv4 and IPv6 script files
    logger.debug(f"INFO - Reading DuckDNS configuration from {DDNS_USER_DUCKDNS_SCRIPT_PATH} and {DDNS_USER_DUCKDNS_V6_SCRIPT_PATH}")
    ipv4_domains, ipv4_token = extract_domain_token(DDNS_USER_DUCKDNS_SCRIPT_PATH)
    ipv6_domains, ipv6_token = extract_domain_token(DDNS_USER_DUCKDNS_V6_SCRIPT_PATH)

    return ipv4_domains, ipv4_token, ipv6_domains, ipv6_token
