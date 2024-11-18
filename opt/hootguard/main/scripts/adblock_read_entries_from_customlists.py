# Script Name: adblock_read_entries_from_customlists.py
# Version: 0.1
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script retrieves entries from either the whitelist or blacklist on the Pi-hole system used in the
# HootGuard setup. It interacts with the Pi-hole API to fetch the list of URLs from custom lists based on 
# the specified list type ('white' for whitelist or 'black' for blacklist). It uses external helper functions 
# to get the active Pi-hole IP address and API key.

import requests
from .pihole_get_api_key import get_pihole_api_key
from .system_get_active_ip_address import get_pihole_ip
from .global_logger import logger

# Function to get the whitelist or blacklist URLs
def get_entires_from_customlists(list_type):
    """Retrieve entries from the specified Pi-hole custom list (whitelist or blacklist)."""
    logger.debug(f"INFO - Retrieving entries from {list_type}list.")    
    
    # Validate the list_type parameter
    if list_type not in ['white', 'black']:
        logger.debug("ERROR - Invalid list_type. Use 'white' for whitelist or 'black' for blacklist.")        
        raise ValueError("Invalid list_type. Use 'white' for whitelist or 'black' for blacklist.")

    # Get the Pi-hole IP address
    pihole_ip = get_pihole_ip()
    if not pihole_ip:
        logger.debug("ERROR - Unable to retrieve Pi-hole IP address.")
        return None  # Unable to retrieve Pi-hole IP address

    # Get the Pi-hole API key
    api_key = get_pihole_api_key()
    if not api_key:
        logger.debug("ERROR - Unable to retrieve Pi-hole API key.")
        return None  # Unable to retrieve API key

    # Pi-hole API URL
    api_url = f"http://{pihole_ip}/admin/api.php"

    # API parameters
    params = {
        'list': list_type,
        'auth': api_key
    }

    # Make the API request
    try:
        logger.debug(f"INFO - Making API request to {api_url} for {list_type}list entries.")
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extract the domains from the response
        entries = [entry['domain'] for entry in data.get('data', [])]
        logger.debug(f"INFO - Retrieved {len(entries)} entries from {list_type}list.")
        return entries
    except requests.exceptions.RequestException as e:
        logger.debug(f"ERROR - API request failed: {str(e)}")
        return None   
