# Script Name: config_loader.py
# Version: 0.2
# Author: HootGuard
# Date: 8. October 2024

# Description:
# This script provides functions to load and extract configuration values from a YAML configuration file.
# The `load_config` function reads the global configuration file (`global_config.yaml`), which is used by the
# HootGuard system. The `get_endpoint_and_secondary_dns` function extracts specific values from the loaded 
# configuration, namely the VPN endpoint and secondary DNS, returning them for further use.

import yaml
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
GLOBAL_CONFIG_FILE_PATH = config['misc']['global_config_file']

# Function to load the YAML configuration file
def load_config():
    with open(GLOBAL_CONFIG_FILE_PATH, 'r') as file:
        return yaml.safe_load(file)

# Function to extract endpoint and secondary_dns
def get_endpoint_and_secondary_dns():
    # Load the configuration
    config = load_config()

    # Extract the values from the YAML
    vpn_endpoint = config['vpn']['endpoint']
    secondary_dns = config['network']['secondary_dns']

    return vpn_endpoint, secondary_dns
