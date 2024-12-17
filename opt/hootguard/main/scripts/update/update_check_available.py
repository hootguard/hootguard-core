# Script Name: update_check_available.py
# Version: 0.2
# Author: HootGuard
# Date: 6. December 2024

# Description:
# This script checks if a new version of the HootGuard system is available by comparing the local version
# with the remote version stored in the configured GitHub repository. The script performs the following tasks:
# 1. Fetches the remote version from a specified URL using the `requests` library.
# 2. Reads the local version from a version file located in the HootGuard system.
# 3. Compares the remote and local versions using semantic version parsing (via the `packaging.version` module).
# 4. If the remote version is newer, it logs the availability of an update and creates an update flag file.
# 5. If the local version is newer or matches the remote version, it removes any existing update flag file.
#
# The script ensures robust error handling, logging, and semantic version comparison for reliable update checks.

import requests
import os
import sys
import logging
from packaging.version import parse  # Import the version parser

# Add the project root directory to the module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from main.scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Configure logging
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

# Define the remote version file URL and local version file path
LOCAL_VERSION_FILE = config['misc']['version_file']
REPO_VERSION_URL = config['update']['repo_version_url']
UPDATE_FLAG_FILE = config['update']['update_available_flag']

def get_remote_version():
    """Fetch the remote version from GitHub."""
    try:
        response = requests.get(REPO_VERSION_URL)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        logging.info(f"Error fetching remote version: {e}")
        return None

def get_local_version():
    """Read the local version from the version file."""
    try:
        with open(LOCAL_VERSION_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        logging.info("Local version file not found.")
        return None

def check_for_update():
    """Compare local and remote versions and set the update flag."""
    remote_version = get_remote_version()
    local_version = get_local_version()

    if not remote_version or not local_version:
        logging.info("Unable to fetch or compare versions.")
        return False

    # Parse versions for proper semantic comparison
    remote_parsed = parse(remote_version)
    local_parsed = parse(local_version)

    if remote_parsed > local_parsed:
        logging.info(f"Update available! Remote version: {remote_version}, Local version: {local_version}")
        with open(UPDATE_FLAG_FILE, "w") as flag:
            flag.write(f"Update available! Remote version: {remote_version}")
        return True
    elif remote_parsed < local_parsed:
        logging.info(f"Local version is newer. Remote version: {remote_version}, Local version: {local_version}")
    else:
        logging.info("No updates available. Local and remote versions match.")

    # Remove the update flag if versions are identical or local is newer
    if os.path.exists(UPDATE_FLAG_FILE):
        os.remove(UPDATE_FLAG_FILE)
    return False

if __name__ == "__main__":
    check_for_update()
