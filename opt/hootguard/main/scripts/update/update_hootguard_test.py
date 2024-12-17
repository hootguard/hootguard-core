# Script Name: update_hootguard.py
# Version: 0.4
# Author: HootGuard
# Date: 12. December 2024

import logging
import sys
import os

# Add the project root directory to the module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from main.scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Configure logging
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

def print_stuff():
    logging.info("--------------- UPDATE PROCESS STARTED ------------------")

def main():
    print_stuff()

if __name__ == "__main__":
    main()
