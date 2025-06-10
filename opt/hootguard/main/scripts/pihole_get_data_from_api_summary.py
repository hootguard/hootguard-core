# Script Name: pihole_get_data_from_api_summary.py
# Version: 0.2
# Author: HootGuard
# Date: 7. October 2024

# Description:
# This script retrieves summary data from the Pi-hole API. It first fetches the Pi-hole IP address and 
# API key, constructs the API request URL, and sends the request to the Pi-hole API. The response is 
# processed to extract specific summary data parameters, which can be specified when calling the 
# `get_data_from_api_summary` function.

import requests
from .pihole_get_api_key import get_pihole_api_key
from .system_get_active_ip_address import get_pihole_ip
from .global_logger import logger

def get_data_from_api_summary(api_params=None):
    """Fetch summary data from the Pi-hole API."""
    logger.debug("INFO - Fetching data from Pi-hole API summary.")

    if api_params is None:
        api_params = []  # Define default value if not provided

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
    api_url = f"http://{pihole_ip}/admin/api.php?summary"
    logger.debug(f"INFO - Constructed Pi-hole API URL: {api_url}")

    # Send request to Pi-hole API with authentication
    response = requests.get(api_url, params={"auth": api_key})

    # Check if request was successful
    if response.status_code == 200:
        summary_data = response.json()
        data = {}
        for param in api_params:
            if param in summary_data:
                data[param] = summary_data[param]
            else:
                data[param] = None  # Parameter not found in API response
        logger.debug("INFO - Data retrieved from Pi-hole API")
        return data
    else:
        logger.debug(f"ERROR - Failed to fetch data from Pi-hole API: {e}")
        return None  # Failed to fetch data from Pi-hole API
