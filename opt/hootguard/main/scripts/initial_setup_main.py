# Script Name: initial_setup_main.py
# Version: 0.3
# Author: HootGuard
# Date: 25. November 2024

# Description:
# This script performs the initial setup for the HootGuard system, ensuring essential configurations 
# are applied and validated. It includes functionalities for:
# - Updating environment and password secret keys.
# - Saving network configurations (IP, subnet, gateway).
# - Generating unique IPv4 and IPv6 addresses for WireGuard interfaces.
# - Generating private keys for WireGuard interfaces.
# - Creating WireGuard configuration files (wg0.conf, wg1.conf).
# - Updating the global configuration file with WireGuard IP settings.
# - Configuring and restarting the production firewall.
# If errors occur during setup, the system resets the VPN configuration to factory defaults.
# A successful setup concludes with a system reboot.

import yaml
import subprocess
import time
from .password_save_and_reboot import password_save_and_reboot_system
from .network_save_configuration_and_reboot import network_save_config_and_reboot
from .initial_setup import is_generate_wireguard_ip_addresses
from .initial_setup import is_update_env_secret_key
from .initial_setup import is_update_password_secret_key
from .initial_setup import is_generate_wireguard_keys
from .initial_setup import is_generate_wireguard_interface_conf
from .initial_setup import is_create_initial_setup_flag_file
from .reset import reset_factory
from .global_logger import logger
from scripts.global_config_loader import load_config

# Load global config
config = load_config()

def perform_initial_setup(ip_v4_address, subnet_mask, standard_gateway, password):
    # If any error occured, this variable will be set to true
    error_occurred = False

    # --- START - Update Pi-hole gravity database
    try:
        logger.debug("INFO - Running 'pihole -g' to update gravity database.")
        subprocess.run(['pihole', '-g'], check=True)
        logger.debug("SUCCESS - Pi-hole gravity updated successfully.")
        error_occurred = False
    except subprocess.CalledProcessError as e:
        logger.debug(f"ERROR - Failed to update Pi-hole gravity database: {str(e)}")
        error_occurred = True
    except Exception as e:
        logger.debug(f"ERROR - Unexpected error during Pi-hole gravity update: {str(e)}")
        error_occurred = True
    # --- END - Update Pi-hole gravity database ---

    # Update the environment secret key (.env)
    if not is_update_env_secret_key.generate_and_update_secret_key():
        logger.info("Error: Failed to update the environment secret key.")
        error_occurred = True

    # Update the password secret key
    if not is_update_password_secret_key.generate_and_replace_secret_key():
        logger.info("Error: Failed to update the password secret key.")
        error_occurred = True

    # Save the password and skip reboot since this is the initial setup
    if not password_save_and_reboot_system(password, True):
        logger.info("Error: Failed to save password and apply the configuration.")
        error_occurred = True

    # Save the ip settings and skip reboot since this is the initial setup
    if not network_save_config_and_reboot(ip_v4_address, subnet_mask, standard_gateway, True):
        logger.info("Error: Failed to save ip settings and apply the configuration.")
        error_occurred = True

    # --- START - IP Address generation ---
    try:
        ipv4_wg0 = is_generate_wireguard_ip_addresses.generate_ipv4()
        ipv6_wg0 = is_generate_wireguard_ip_addresses.generate_ipv6()
        ipv4_wg1 = is_generate_wireguard_ip_addresses.generate_ipv4()
        ipv6_wg1 = is_generate_wireguard_ip_addresses.generate_ipv6()

        if not ipv4_wg0 or not ipv6_wg0 or not ipv4_wg1 or not ipv6_wg1:
            raise ValueError("Failed to generate valid IP addresses.")

    except Exception as e:
        logger.info(f"Error: {e}")
        error_occurred = True

    # Ensure IPv4 addresses for wg0 and wg1 are not identical
    max_attempts = 10  # Limit attempts to avoid infinite loops
    attempts = 0
    while ipv4_wg0 == ipv4_wg1:
        logger.debug("Collision detected for IPv4. Regenerating IP for wg1.")
        ipv4_wg1 = is_generate_wireguard_ip_addresses.generate_ipv4()
        attempts += 1
        if attempts >= max_attempts:
            logger.info("Error: Failed to generate unique IPv4 addresses after multiple attempts.")
            error_occurred = True

    # Ensure IPv6 addresses for wg0 and wg1 are not identical
    attempts = 0
    while ipv6_wg0 == ipv6_wg1:
        print("Collision detected for IPv6. Regenerating IP for wg1.")
        ipv6_wg1 = is_generate_wireguard_ip_addresses.generate_ipv6()
        attempts += 1
        if attempts >= max_attempts:
            print("Error: Failed to generate unique IPv6 addresses after multiple attempts.")
            # return False
            error_occurred = True

    logger.info(f"IP addresses for both wireguard interfaces successfully generated")
    # --- END - IP Address generation ---

    # --- START - Key Generation for WireGuard Interfaces ---
    try:
        private_key_wg0 = is_generate_wireguard_keys.generate_wireguard_keys("wg0")
        private_key_wg1 = is_generate_wireguard_keys.generate_wireguard_keys("wg1")

        if not private_key_wg0 or not private_key_wg1:
            raise ValueError("Failed to generate private keys for WireGuard interfaces.")

    except Exception as e:
        logger.info(f"Error generating WireGuard keys: {e}")
        error_occurred = True
    # --- END - Key Generation for WireGuard Interfaces ---

    # --- START - WireGuard Configuration File Creation ---
    try:
        # Create configuration file wg0.conf for WireGuard interface
        if not is_generate_wireguard_interface_conf.create_wireguard_conf("wg0", private_key_wg0, ipv4_wg0, ipv6_wg0):
            raise ValueError("Failed to generate wg0 configuration file.")

        # Clear the private key for wg0 after usage
        private_key_wg0 = None

        # Create configuration file wg1.conf for WireGuard interface
        if not is_generate_wireguard_interface_conf.create_wireguard_conf("wg1", private_key_wg1, ipv4_wg1, ipv6_wg1):
            raise ValueError("Failed to generate wg1 configuration file.")

        # Clear the private key for wg1 after usage
        private_key_wg1 = None

    except Exception as e:
        logger.error(f"Error creating WireGuard configuration files: {e}")
        # return False
        error_occurred = True
    # --- END - WireGuard Configuration File Creation ---

    # Replace wireguard ip address data in global_config file
    try:
        with open(config['misc']['global_config_file'], 'r') as file:
            config_data = yaml.safe_load(file)

        # Replace entries with ip data
        config_data['vpn']['wireguard_interface_1_v4_ip_addresse'] = ipv4_wg0
        config_data['vpn']['wireguard_interface_1_v6_ip_addresse'] = ipv6_wg0
        config_data['vpn']['wireguard_interface_2_v4_ip_addresse'] = ipv4_wg1
        config_data['vpn']['wireguard_interface_2_v6_ip_addresse'] = ipv6_wg1

        with open(config['misc']['global_config_file'], 'w') as file:
            yaml.dump(config_data, file)

        logger.info("Global config replaced with ip data.")
        error_occurred = False
    except Exception as e:
        logger.error(f"Failed to update global config: {e}")
        error_occurred = True

    # --- START - Firewall configuration and restart
    # Activate production firewall and restart the netfilter to activate the rules
    try:
        # Use subprocess to run the shell script
        result = subprocess.run(['/usr/bin/sudo', 'bash', config['vpn']['iptables_settings_file']], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Restart the netfilter-persistent service to make the rules persistent
        subprocess.run(['/usr/bin/sudo', 'systemctl', 'restart', 'netfilter-persistent'], check=True)

        logger.info("Production firewall rules were successfully set and service restarted")
        error_occurred = False

    except subprocess.CalledProcessError as e:
        # Handle errors if the script execution fails
        logger.error("Error activating production firewall rules occurred while running the script:")
        print(e.stderr)
        error_occurred = True
    # --- END - Firewall configuration and restart



    # If any error occurred during the process, reset the VPN configuration
    if error_occurred:
        logger.error("Errors detected. Running factory reset...")
        reset_factory.reset_vpn_configurations("initial_setup")
        return False
    if not error_occurred:
        logger.info("Initial setup successful - Rebooting system")
        is_create_initial_setup_flag_file.create_init_flag()
        # Return True if everything was successful
        system_reboot()
        return True

def system_reboot():
    """Reboot the system to apply the new configuration."""
    try:
        logger.info("INFO - Rebooting the system.")
        # Execute the reboot command
        subprocess.call(['/usr/bin/sudo', 'reboot'])
    except Exception as e:
        logger.error(f"ERROR - Error during reboot: {e}")
