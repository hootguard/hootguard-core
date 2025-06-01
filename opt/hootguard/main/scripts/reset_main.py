# Script Name: reset_main.py
# Version: 0.2
# Author: HootGuard
# Date: 14. October 2024

# Description:
# This script performs a full factory reset or a targeted reset (based on the input option) 
# of the HootGuard system. It offers two reset options:
# 1. 'reset_button': This option resets the IP address and web/Pi-hole passwords to default values, 
#    after which the system is rebooted.
# 2. 'factory_reset': This option resets VPN configurations, DDNS settings, and other system-level 
#    configurations, followed by a system reboot.
#
# Both options ensure the system is rebooted after a successful reset to apply changes.
# The script also logs important events and errors during the process using the global logger.

import subprocess
from .global_logger import logger
from .reset import reset_ip_address_and_password
from .reset import reset_factory
from .system_reboot import reboot

def perform_reset(reset_option):
    if reset_option == "reset_button":
        if reset_ip_address_and_password.reset_ip_and_password():
            reboot()
    elif reset_option == "factory_reset":
        if reset_factory.reset_vpn_configurations():
            reboot()
