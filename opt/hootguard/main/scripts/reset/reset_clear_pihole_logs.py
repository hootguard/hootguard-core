import subprocess
import os
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()


def clear_pihole_logs():
    try:
        # Clear DNS query log
        subprocess.run(['sudo', 'truncate', '-s', '0', '/var/log/pihole.log'], check=True)
        
        # Clear FTL log
        subprocess.run(['sudo', 'truncate', '-s', '0', '/var/log/pihole-FTL.log'], check=True)

        # Stop the FTL service
        subprocess.run(['sudo', 'service', 'pihole-FTL', 'stop'], check=True)
        # Remove the Pi-hole FTL database
        subprocess.run(['sudo', 'rm', '/etc/pihole/pihole-FTL.db'], check=True)
        # Restart the FTL service, which will regenerate the database
        subprocess.run(['sudo', 'service', 'pihole-FTL', 'start'], check=True)

        # If everything runs fine, return True
        logger.info("Pi-hole logs and FTL database were successfully removed")
        return True

    except Exception as e:
        # Print the error for debugging
        logger.info(f"Error occured while deleting pi-hole logs: {e}")
        
        # Return False if any error occurs
        return False
