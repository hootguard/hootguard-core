# Script Name: reset_clear_system_logs.py
# Version: 0.2
# Author: HootGuard
# Date: 10. January 2025

# Description:
# This script truncates various system logs and deletes all `.gz` files in the `/var/log` directory 
# and its subdirectories. Additionally, it clears the shell history to ensure a clean reset of the 
# system logs in the HootGuard setup. It includes:
# - Truncation of log files such as `/var/log/auth.log`, `/var/log/syslog`, and others.
# - Deletion of `.gz` compressed log files.
# - Clearing of shell history using the `history -c` command.
# The script logs the success or failure of each operation and returns `True` on success or `False` 
# if any error occurs.

import glob
import subprocess
from scripts.global_logger import logger

def clear_system_logs():
    try:
        # List of log patterns to truncate
        log_patterns = [
            "/var/log/auth.log*",
            "/var/log/daemon.log*",
            "/var/log/debug*",
            "/var/log/kern.log*",
            "/var/log/messages*",
            "/var/log/syslog*",
            "/var/log/user.log*",
            "/var/log/alternatives.log*",
            "/var/log/dpkg.log*",
            "/var/log/faillog",
            "/var/log/lastlog",
            "/var/log/btmp*",
            "/var/log/wtmp*",
        ]

        # Truncate log files with sudo
        for pattern in log_patterns:
            for file_path in glob.glob(pattern):
                subprocess.run(
                    ["/usr/bin/sudo", "truncate", "-s", "0", file_path],
                    check=True
                )
                logger.info(f"Truncated: {file_path}")

        # Delete .gz files in /var/log and subdirectories with sudo
        for gz_file in glob.glob("/var/log/**/*.gz", recursive=True):
            subprocess.run(
                ["/usr/bin/sudo", "rm", "-f", gz_file],
                check=True
            )
            logger.info(f"Deleted: {gz_file}")

        # Clear shell history with sudo
        subprocess.run(["bash", "-c", "history -c"], check=True)
        logger.info("Shell history cleared.")

        return True  # Return True if everything is successful

    except Exception as e:
        logger.info(f"An error occurred: {e}")
        return False  # Return False if any error occurs
