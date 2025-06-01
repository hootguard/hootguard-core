# Script Name: config_loader.py
# Version: 0.1
# Author: HootGuard
# Date: 8. October 2024

# Description:
# This utility script provides a function to load the global YAML configuration file used by the HootGuard system.
# It ensures that the configuration can be easily loaded and accessed across multiple scripts, providing a centralized
# location for configuration management. The function reads the YAML file and returns the parsed configuration as a dictionary.

import yaml

# Function to load the YAML configuration file
def load_config():
    with open('/opt/hootguard/misc/global_config.yaml', 'r') as file:
        return yaml.safe_load(file)
