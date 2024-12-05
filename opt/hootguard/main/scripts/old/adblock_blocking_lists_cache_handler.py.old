# Script Name: adblock_blocking_lists_cache_handler.py.py
# Version: 0.4
# Author: HootGuard
# Date: 16 November 2024

# Description:
# This script provides functionality for caching remote resources locally to optimize performance
# and reduce reliance on external resources (e.g., GitHub). It is designed to cache files based on
# a unique key (e.g., profile names) and associated URLs. If the cached file is valid (not expired),
# it is reused; otherwise, the data is fetched from the URL and the cache is updated.

import os
import time
import requests
from .global_logger import logger
from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
CACHE_DIR = config['adblock']['cache_path']
# Configuration
CACHE_EXPIRY = 7 * 24 * 60 * 60  # One week in seconds

def fetch_with_cache(cache_key, url):
    """
    Fetch data from a cache or a remote URL if the cache is invalid.
    
    Args:
        cache_key (str): The unique identifier for the cached file.
        url (str): The URL to fetch data from if the cache is invalid.
    
    Returns:
        str: The content of the cached file or fetched data.
    """
    # Ensure the cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)

    # Construct the cache file path
    cache_file = os.path.join(CACHE_DIR, f"{cache_key}.txt")

    # Check if the cache exists and is still valid
    if os.path.exists(cache_file):
        cache_age = time.time() - os.path.getmtime(cache_file)
        if cache_age < CACHE_EXPIRY:
            logger.debug(f"INFO - Using cached data for key: {cache_key}")
            with open(cache_file, "r") as f:
                return f.read()

    # Fetch data from the URL if the cache is missing or expired
    logger.debug(f"INFO - Fetching data from URL for key: {cache_key}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text

        # Save the data to the cache
        with open(cache_file, "w") as f:
            f.write(data)

        return data
    except requests.RequestException as e:
        logger.debug(f"ERROR - Failed to fetch data for key '{cache_key}': {e}")
        return None
