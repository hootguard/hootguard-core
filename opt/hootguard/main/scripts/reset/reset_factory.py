# Script Name: reset_factory.py
# Version: 0.8
# Author: HootGuard
# Date: 11. January 2025

# Description:
# This script performs a factory reset for the HootGuard system, clearing all VPN configurations, keys, and logs,
# while resetting system settings to defaults. Key actions include:
# - Deleting VPN client configurations, QR codes, and client keys.
# - Clearing VPN client database tables and WireGuard keys/configurations.
# - Resetting IP, password, and DDNS settings to default or dummy values.
# - Removing traffic control rules and activating factory firewall rules.
# - Updating the global configuration file with dummy data.
# - Clearing Pi-hole logs and updating Adblock status.
# The script ensures the system is fully reset to its factory state, ready for reconfiguration.
# Returns `True` on success, `False` on failure.

import os
import shutil
import sqlite3
import subprocess
import time
import threading
import yaml
from .reset_ip_address_and_password import reset_ip_and_password
from .reset_delete_wg_keys_and_configs import delete_wg_keys_and_configs
from .reset_clear_pihole_logs import clear_pihole_logs
from .reset_clear_system_logs import clear_system_logs
from scripts.initial_setup import is_update_env_secret_key
from scripts.ssh_control_service import disable_ssh
from scripts.ddns_configure_user_dynu import ddns_write_and_activate_dynu
from scripts.ddns_update_status_file import ddns_update_status
from scripts.ddns_change_crontab import ddns_update_crontab
from scripts.snooze_update_status_file import snooze_update_time
from scripts.adblock_update_status_file import update_status_file
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load global config
config = load_config()

# Paths from the config
STATIC_QR_PATH = config['vpn']['client_qrcode_path']
VPN_CONFIG_PATH = config['vpn']['client_configs_path']
VPN_CLIENT_KEYS_PATH = config['vpn']['client_keys_path']
VPN_DB_PATH = config['vpn']['client_db_path']
WG_INT_1 = config['vpn']['wireguard_interface_1'] # Default wg0
WG_PRIVATEKEY_WG0_PATH = config['vpn']['wireguard_wg0_privatekey_path']
WG_PUBLICKEY_WG0_PATH = config['vpn']['wireguard_wg0_publickey_path']
WG_INT_2 = config['vpn']['wireguard_interface_2'] # Default wg1
WG_PRIVATEKEY_WG1_PATH = config['vpn']['wireguard_wg1_privatekey_path']
WG_PUBLICKEY_WG1_PATH = config['vpn']['wireguard_wg1_publickey_path']
WG_MAIN_PATH = config['vpn']['wireguard_main_path']
GLOBAL_CONFIG_PATH = config['misc']['global_config_file']
WG_CONF_WG0_PATH = os.path.join(WG_MAIN_PATH, f"{WG_INT_1}.conf")
WG_CONF_WG1_PATH = os.path.join(WG_MAIN_PATH, f"{WG_INT_2}.conf")
GLOBAL_LOGGING_PATH = config['logging']['global_logging_file_path']
SECURE_RUN_FILE = config['misc']['secure_run_file']
IPTABLES_FACTORY_RESET_FILE = config['misc']['iptables_factory_reset_file']
ADBLOCK_STATUS_PATH = config['adblock']['status_path']
ADBLOCK_DB_PATH = config['adblock']['db_path']
ADBLOCK_BLOCKLIST_URLS = config['adblock']['blocklist_urls']

#def clear_secret_file(file_path):
#    """Erases the content of the file (.env and secret.key) but keeps the file itself."""
#    try:
#        # Open the file in write mode, which will truncate (erase) its contents
#        with open(file_path, 'w') as file:
#            # Writing nothing to the file, which effectively erases the content
#            pass
#        print(f"File {file_path} content erased successfully.")
#    except Exception as e:
#        print(f"Error erasing content of the file {file_path}: {e}")

# Delete all .png files in /opt/hootguard/main/static
def delete_qr_codes():
    try:
        for file in os.listdir(STATIC_QR_PATH):
            if file.endswith(".png"):
                os.remove(os.path.join(STATIC_QR_PATH, file))
        logger.info("QR code files deleted successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to delete QR code files: {e}")
        return False

# Delete all .conf files in /opt/hootguard/vpn/configs
def delete_vpn_configs():
    try:
        for file in os.listdir(VPN_CONFIG_PATH):
            if file.endswith(".conf"):
                os.remove(os.path.join(VPN_CONFIG_PATH, file))
        logger.info("VPN client config files deleted successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to delete VPN client config files: {e}")
        return False

# Clear the content of "all_vpn_clients" and "temp_vpn_clients" tables
def clear_vpn_clients_db():
    try:
        conn = sqlite3.connect(VPN_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM all_vpn_clients")
        cursor.execute("DELETE FROM temp_vpn_clients")
        conn.commit()
        conn.close()
        logger.info("VPN client tables cleared successfully.")
        return True
    except sqlite3.Error as e:
        logger.error(f"Failed to clear VPN client tables: {e}")
        return False

# Delete all files from /etc/wireguard/client_keys
def delete_client_keys():
    try:
        for file in os.listdir(VPN_CLIENT_KEYS_PATH):
            os.remove(os.path.join(VPN_CLIENT_KEYS_PATH, file))
        logger.info("Client key files deleted successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to delete client key files: {e}")
        return False

# Update adblock status file to "normal" and update the gravity database
def adblock_update_status_file_and_update_gravity_db():
    try:
        # 1. Write "normal" into the status file
        logger.info("INFO - Writing 'normal' to Adblock status file.")
        with open(ADBLOCK_STATUS_PATH, "w") as file:
            file.write("normal\n")
        logger.info("SUCCESS - Adblock status file updated with 'normal'.")

        # 2. Connect to the gravity database
        with sqlite3.connect(ADBLOCK_DB_PATH) as conn:
            cur = conn.cursor()
            # Clear all existing entries from adlist before adding the "normal" blocklist
            logger.info("INFO - Deleting all existing entries from adlist table.")
            cur.execute("DELETE FROM adlist;")

            # Insert the "normal" blocklist URL
            normal_url = ADBLOCK_BLOCKLIST_URLS.get("normal")
            if normal_url:
                cur.execute("INSERT OR IGNORE INTO adlist (address) VALUES (?);", (normal_url,))
                logger.info("SUCCESS - 'normal' blocklist URL added to adlist.")
            else:
                logger.info("ERROR - No URL defined for 'normal' blocklist. Cannot proceed.")
                return False

            # Commit the changes to the database
            conn.commit()

        # 3. Update Pi-hole Gravity database
        logger.info("INFO - Running 'pihole -g' to update gravity database.")
        subprocess.run(['pihole', '-g'], check=True)
        logger.info("SUCCESS - Pi-hole gravity updated successfully.")

        return True
    except sqlite3.DatabaseError as e:
        logger.error(f"ERROR - Database error while updating blocking lists: {str(e)}")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"ERROR - Failed to update Pi-hole gravity database: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"ERROR - Unexpected error: {str(e)}")
        return False

# Remove traffic control from wg1 interface
def remove_traffic_control():
    """Clear traffic control rules for wg1 interface."""
    try:
        result = subprocess.run(
            ['/usr/bin/sudo', SECURE_RUN_FILE, 'clear-traffic-control', 'wg1'],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        logger.info(f"Traffic control removed: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to remove traffic control from wg1: {e}")
        return False

# Replace entries in global_config.yaml with dummy data
def replace_global_config():
    try:
        with open(GLOBAL_CONFIG_PATH, 'r') as file:
            config_data = yaml.safe_load(file)

        # Replace entries with dummy data
        config_data['network']['interface_1_v4_ip_address'] = '192.168.0.250/24'
        config_data['network']['interface_1_v4_network'] = '192.168.0.0/24'
        config_data['network']['interface_1_v6_ip_address'] = '2a02:abcd:1337:c001:d00d:face:b00c:1234/64'
        config_data['network']['primary_dns'] = '192.168.0.250'
        config_data['vpn']['endpoint'] = 'dummy.yourdns.com'
        config_data['vpn']['wireguard_interface_1_v4_ip_addresse'] = '10.0.0.0/24'
        config_data['vpn']['wireguard_interface_1_v6_ip_addresse'] = 'fd00:::/64'
        config_data['vpn']['wireguard_interface_2_v4_ip_addresse'] = '10.0.1.0/24'
        config_data['vpn']['wireguard_interface_2_v6_ip_addresse'] = 'fd01::/64'

        with open(GLOBAL_CONFIG_PATH, 'w') as file:
            yaml.dump(config_data, file)

        logger.info("Global config replaced with dummy data.")
        return True
    except Exception as e:
        logger.error(f"Failed to update global config: {e}")
        return False

# Delete the flag files (SSH / initial setup)
def delete_flag_file(file_path):
    try:
        # Check if the file exists
        if os.path.exists(file_path):
            # Delete the file
            os.remove(file_path)
            print(f"Deleted: {file_path}")
            return True
        else:
            print(f"File not found: {file_path}")
            return True # Returns true since if file does not exists, it was already deleted and wil not stop the script from completion.
    except Exception as e:
        print(f"Error occurred while deleting the file: {e}")
        return False

# Reset the ssh password back to the defaul password
# NOTE: The default password is public and intended for initial setup only.
def reset_ssh_password_to_default():
    """Reset the ssh password to the default password"""
    user = 'hootguard'
    default_password = 'HootGuard'
    try:
        result = subprocess.run(
            ['/usr/bin/sudo', SECURE_RUN_FILE, 'set-password', user, default_password],
            capture_output=True, text=True, check=True
        )
        logger.info(f"SSH password reset to default for user {user}: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error resetting SSH password for user {user}: {e.stderr.strip()}")
        return False


# Clear existing firewall rules and configure factory reset iptable rules
def activate_factory_reset_firewall():
    """Reset firewall rules to factory defaults."""
    try:
        result = subprocess.run(
            ['/usr/bin/sudo', SECURE_RUN_FILE, 'reset-firewall', IPTABLES_FACTORY_RESET_FILE],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        logger.info(f"Firewall successfully reset: {result.stdout}")
        return True  # Return True if the script ran successfully

    except subprocess.CalledProcessError as e:
        print(f"Failed to reset firewall: {e.stderr}")
        return False  # Return False if an error occurred

# Empty the hootguard log file
def reset_hootguard_log_file():
    try:
        # Open the log file in write mode, which will truncate the file to zero length
        with open(GLOBAL_LOGGING_PATH, 'w') as file:
            # Do nothing, opening in 'w' mode will automatically clear the file content
            pass

        logger.info("INFO - HootGuard logfiles successfully emptied")
        return True
    except Exception as e:
        logger.error(f"ERROR - Error while deleting HootGuard logging file: {e}")
        return False

# Execute all steps
# If the initial_setup fails, the reset_vpn_configuration will run to set back everything to factory settings, only the loggings will not be deleted.
def reset_vpn_configurations(initial_setup=None):
    try:
        # Reset IP and password
        if not reset_ip_and_password():
            return False

        # Generate new secret key
        if not is_update_env_secret_key.generate_and_update_secret_key(): # /opt/hootguard/.env file - Write new .env secret
            return False

        # Delete QR codes
        if not delete_qr_codes(): # /opt/hootguard/main/static
            return False

        # Delete VPN configs
        if not delete_vpn_configs(): # /opt/hootguard/vpn/configs
            return False

        # Clear VPN clients DB
        if not clear_vpn_clients_db(): # /opt/hootguard/vpn/vpn_clients.db
            return False

        # Delete client keys
        if not delete_client_keys(): # /etc/wireguard/client_keys
            return False

        # Delete WireGuard keys and config files
        if not delete_wg_keys_and_configs(): # Delete all wireguard keys and config files (priv + pub key + interface config)
            return False

        # Reset the snooze time back to 5 minues (300 seconds)
        if not snooze_update_time(300):
            return False

        ### DYNU
        if not ddns_write_and_activate_dynu('xxx', 'xxx', "ipv4", True): # Delete Dynu configuration for IPv4
            return False

        if not ddns_write_and_activate_dynu('xxx', 'xxx', "ipv6", True): # Delete Dynu configuration for IPv6
            return False

        ### NO CONFIG
        if not ddns_update_status("no-config"): # Reset ddns status
            return False

        if not ddns_update_crontab("no-config"): # Delete all ddns crontab entries
            return False

        # Adblock update status and gravity DB
        if not adblock_update_status_file_and_update_gravity_db(): # Set adblock status file to normal and update database
            return False

        # Remove traffic control
        if not remove_traffic_control():
            return False

        # Delete SSH first-time flag
        if not delete_flag_file(config['ssh']['first_time_flag_path']): # /opt/hootguard/misc/ssh_first_time_flag
            return False

        # Delete initial setup flag
        if not delete_flag_file(config['misc']['init_flag']): # /opt/hootguard/misc/init_flag
            return False

        # Reset ssh password to default
        if not reset_ssh_password_to_default():
            return False

        # Disable SSH
        if not disable_ssh():
            return False

        # Clear pi-hole logs and database
        if not clear_pihole_logs():
            return False

        # Clear system logs and delete .gz log archived files
        if not clear_system_logs():
            return False

        # Clear existing firewall rules and activate basic factory firewall rules
        if not activate_factory_reset_firewall():
            return False

        # Do not delete login it initial_setup calls function
        # Reset hootguard logging file
        if not initial_setup:
            if not reset_hootguard_log_file(): # /var/log/hootguard_system.log
                return False

        # Replace global config with dummy data
        if not replace_global_config():
            return False

        # If everything is successful, return True
        print("Factory reset was successfully performed - restarting system...")
        return True

    except Exception as e:
        logger.error(f"Error during reset_vpn_configurations (reset_factory): {e}")
        return False
