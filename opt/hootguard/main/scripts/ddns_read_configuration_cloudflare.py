# Script Name: ddns_read_configuration_cloudflare.py
# Version: 0.4
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script reads the Cloudflare DDNS configuration from the 'user-cloudflare.sh' and 'user-cloudflarev6.sh' files.
# It extracts the authentication email, authentication key, zone identifier, and record name for both IPv4 and IPv6.
# The extracted data is returned for further processing by the HootGuard system. This version includes logging to
# track the process of reading and extracting configuration values.

import re
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_CLOUDFLARE_SCRIPT_PATH = config['ddns']['user_cloudflare_script']
DDNS_USER_CLOUDFLARE_V6_SCRIPT_PATH = config['ddns']['user_cloudflare_v6_script']

def ddns_read_config_cloudflare():
    """Read the Cloudflare DDNS configuration for both IPv4 and IPv6."""
    logger.debug(f"INFO - Reading Cloudflare DDNS configuration from {DDNS_USER_CLOUDFLARE_SCRIPT_PATH} and {DDNS_USER_CLOUDFLARE_V6_SCRIPT_PATH}")

    auth_email = None
    auth_key = None
    zone_identifier = None
    record_name = None
    auth_email_v6 = None
    auth_key_v6 = None
    zone_identifier_v6 = None
    record_name_v6 = None

# Read IPv4 Cloudflare configuration
    logger.debug(f"INFO - Reading IPv4 Cloudflare configuration from {DDNS_USER_CLOUDFLARE_SCRIPT_PATH}")
    try:
        with open(DDNS_USER_CLOUDFLARE_SCRIPT_PATH, 'r') as file:
            content = file.read()

            auth_email_match = re.search(r'auth_email="(.*?)"', content)
            if auth_email_match:
                auth_email = auth_email_match.group(1)

            auth_key_match = re.search(r'auth_key="(.*?)"', content)
            if auth_key_match:
                auth_key = auth_key_match.group(1)

            zone_identifier_match = re.search(r'zone_identifier="(.*?)"', content)
            if zone_identifier_match:
                zone_identifier = zone_identifier_match.group(1)

            record_name_match = re.search(r'record_name="(.*?)"', content)
            if record_name_match:
                record_name = record_name_match.group(1)

        logger.debug(f"INFO - Extracted IPv4 Cloudflare configuration: {auth_email}, {zone_identifier}, {record_name}")
    except FileNotFoundError as e:
        logger.debug(f"ERROR - IPv4 Cloudflare configuration file not found: {str(e)}")

    # Read IPv6 Cloudflare configuration
    logger.debug(f"INFO - Reading IPv6 Cloudflare configuration from {DDNS_USER_CLOUDFLARE_V6_SCRIPT_PATH}")
    try:
        with open(DDNS_USER_CLOUDFLARE_V6_SCRIPT_PATH, 'r') as file:
            content = file.read()

            auth_email_match = re.search(r'auth_email="(.*?)"', content)
            if auth_email_match:
                auth_email_v6 = auth_email_match.group(1)

            auth_key_match = re.search(r'auth_key="(.*?)"', content)
            if auth_key_match:
                auth_key_v6 = auth_key_match.group(1)

            zone_identifier_match = re.search(r'zone_identifier="(.*?)"', content)
            if zone_identifier_match:
                zone_identifier_v6 = zone_identifier_match.group(1)

            record_name_match = re.search(r'record_name="(.*?)"', content)
            if record_name_match:
                record_name_v6 = record_name_match.group(1)

        logger.debug(f"INFO - Extracted IPv6 Cloudflare configuration: {auth_email_v6}, {zone_identifier_v6}, {record_name_v6}")
    except FileNotFoundError as e:
        logger.debug(f"ERROR - IPv6 Cloudflare configuration file not found: {str(e)}")

    return auth_email, auth_key, zone_identifier, record_name, auth_email_v6, auth_key_v6, zone_identifier_v6, record_name_v6
