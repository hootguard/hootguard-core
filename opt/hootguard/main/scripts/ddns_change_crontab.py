# Script Name: ddns_change_crontab.py
# Version: 1.3
# Author: HootGuard
# Date: 10. September 2024

# Description:
# This script manages Dynamic DNS (DDNS) updates within the system's crontab. It supports adding, updating, 
# or completely removing DDNS-related cron jobs based on the specified DDNS type. 
# If the 'no-config' type is specified, the script will remove all DDNS jobs to disable the functionality.
# For other types, it will remove any existing jobs and add a new one, which runs every 5 minutes.
# The script utilizes the `CronTab` module to interact with the user's crontab.

from crontab import CronTab
from .global_logger import logger

from .global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
DDNS_USER_HOOTDNS_COMMAND = config['ddns']['user_hootdns_command']
DDNS_USER_HOOTDNS_V6_COMMAND = config['ddns']['user_hootdns_v6_command']
DDNS_USER_DYNU_COMMAND = config['ddns']['user_dynu_command']
DDNS_USER_DYNU_V6_COMMAND = config['ddns']['user_dynu_v6_command']

def ddns_update_crontab(ddns_type):
    """
    Updates or removes a DDNS job from the crontab based on the specified ddns_type.

    Parameters:
    - ddns_type (str): The type of DDNS to update or remove from the crontab.

    Returns:
    - str: A message indicating the outcome of the operation.
    """
    # Load the current user's crontab
    cron = CronTab(user=True)
    logger.debug(f"INFO - Loaded the crontab for the current user.")

    # Remove all existing DDNS jobs, regardless of the ddns_type
    cron.remove_all(comment='DDNSUpdate')
    cron.remove_all(comment='DDNSUpdateIPv4')
    cron.remove_all(comment='DDNSUpdateIPv6')
    logger.debug(f"INFO - Removed all existing DDNS jobs (IPv4 and IPv6) from the crontab.")

    # If 'no-config', just remove all jobs and stop further execution
    if ddns_type == "no-config":
        cron.write()
        logger.debug(f"SUCCESS - All DDNS jobs have been removed as 'no-config' was specified.")
        return "All DDNS jobs have been removed from the crontab."

    # Mapping of ddns_type to the corresponding command and comment
    ddns_commands = {
        'user-hootdns-ipv6': (DDNS_USER_HOOTDNS_V6_COMMAND, 'DDNSUpdateIPv6'),
        'user-hootdns-ipv4': (DDNS_USER_HOOTDNS_COMMAND, 'DDNSUpdateIPv4'),
        'user-dynu-ipv6': (DDNS_USER_DYNU_V6_COMMAND, 'DDNSUpdateIPv6'),
        'user-dynu-ipv4': (DDNS_USER_DYNU_COMMAND, 'DDNSUpdateIPv4')
    }

    if ddns_type in ddns_commands:
        command, comment = ddns_commands[ddns_type]
        logger.debug(f"INFO - DDNS type '{ddns_type}' detected. Preparing to add cron job with comment: {comment}")

        # Remove any previous jobs for the same comment (already done above)
        cron.remove_all(comment=comment)

        # Add the new job with a unique comment for easy identification
        job = cron.new(command=command, comment=comment)
        job.setall('*/5 * * * *')
        logger.debug(f"INFO - Added a new cron job for '{ddns_type}' to run every 5 minutes with command: {command}")
    else:
        logger.debug(f"ERROR - Invalid DDNS type: {ddns_type}")
        return False

    # Write changes to the crontab
    cron.write()
    logger.info(f"INFO - Cron job for '{ddns_type}' has been updated successfully.")
    return True
