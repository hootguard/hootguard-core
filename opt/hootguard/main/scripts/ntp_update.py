import subprocess
import logging
import sys
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load global config
config = load_config()

# Fetch NTP servers from the configuration
NTP_SERVERS = config['ntp']['servers']

def sync_time(ntp_server):
    """
    Attempt to synchronize the system time using ntpdate with the given NTP server.
    """
    try:
        logger.info(f"Attempting to sync time with NTP server: {ntp_server}")
        result = subprocess.run(
            ["/usr/bin/sudo", "/usr/sbin/ntpdate", ntp_server],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30  # Add a timeout for security
        )
        if result.returncode == 0:
            logger.info(f"Time synchronized successfully with {ntp_server}.")
            print(f"Time synchronized successfully with {ntp_server}.")
            return True
        else:
            logger.warning(f"Failed to sync time with {ntp_server}: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout occurred while trying to sync with {ntp_server}.")
    except Exception as e:
        logger.error(f"Error while trying to sync with {ntp_server}: {e}")
    return False

def update_ntp_server():
    """
    Synchronize system time with NTP servers.
    """
    if not NTP_SERVERS:
        logger.error("No NTP servers found in configuration.")
        sys.exit(1)

    for server in NTP_SERVERS:
        if sync_time(server):
            return True
    else:
        logger.error("Failed to sync time with all NTP servers.")
        return False

if __name__ == "__main__":
    update_ntp_server()
