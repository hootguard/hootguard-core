# Script Name: update_hootguard.py
# Version: 0.3
# Author: HootGuard
# Date: 6. December 2024

# Description:
# This script automates the update process for the HootGuard system. It performs the following tasks:
# 1. Backs up critical system directories and files to ensure recovery in case of an update failure.
# 2. Pulls or clones the latest version of the HootGuard repository from the configured GitHub URL.
# 3. Synchronizes updated files from the repository to their respective system locations using rsync.
# 4. Applies correct permissions and ownership to critical files for system security.
# 5. Validates configurations like sudoers and web server settings to prevent errors post-update.
# 6. Restarts all necessary services to apply changes.
# 7. Cleans up temporary files and validates that services are running correctly post-update.
#
# The script ensures robust logging at each step, making it easy to debug issues or monitor the update process.

import os
import subprocess
import sys
import logging

# Add the project root directory to the module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from main.scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Configure logging
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

# Define the remote version file URL and local version file path
REPO_URL = config['update']['repo_url']
LOCAL_REPO_PATH = config['update']['local_repo_path']
UPDATE_FLAG_FILE = config['update']['update_flag']
BACKUP_PATH = "/opt/hootguard/backup"

CURRENT_PATHS = {
    "etc": "/etc",
    "opt_hootguard": "/opt/hootguard",
    "var_www_html": "/var/www/html",
    "usr_local_bin": "/usr/local/bin",
    "boot": "/boot"
}

def run_command(command):
    """Execute a shell command and handle errors."""
    try:
        subprocess.run(command, check=True, shell=True)
        logging.info(f"Successfully executed: {command}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing {command}: {e}")
        return False

def create_backup():
    """Create a backup of current system files."""
    os.makedirs(BACKUP_PATH, exist_ok=True)
    for folder, dest in CURRENT_PATHS.items():
        backup_dest = os.path.join(BACKUP_PATH, os.path.basename(dest))
        logging.info(f"Backing up {dest} to {backup_dest}...")
        if not run_command(f"rsync -a {dest}/ {backup_dest}/"):
            logging.error(f"Failed to back up {dest}")
            return False
    return True

def update_repository():
    """Clone or pull the latest changes from the repository."""
    if os.path.exists(LOCAL_REPO_PATH):
        logging.info("Pulling latest changes from repository...")
        return run_command(f"git -C {LOCAL_REPO_PATH} pull")
    else:
        logging.info("Cloning repository for the first time...")
        return run_command(f"git clone {REPO_URL} {LOCAL_REPO_PATH}")

def copy_files():
    """Synchronize updated files to their respective locations."""
    for folder, dest in CURRENT_PATHS.items():
        source_path = os.path.join(LOCAL_REPO_PATH, folder)
        if os.path.exists(source_path):
            logging.info(f"Updating {dest} from {source_path}...")
            if not run_command(f"rsync -a {source_path}/ {dest}/"):
                logging.error(f"Failed to copy files from {source_path} to {dest}")
                return False
    return True

def apply_permissions():
    """Apply correct permissions to critical files."""
    permissions = [
        ("chmod 0440 /etc/sudoers.d/hootguard", "/etc/sudoers.d/hootguard"),
        ("chown root:root /etc/sudoers.d/hootguard", "/etc/sudoers.d/hootguard"),
    ]
    for cmd, file_path in permissions:
        if os.path.exists(file_path):
            logging.info(f"Applying permissions: {cmd}")
            if not run_command(cmd):
                logging.error(f"Failed to apply permissions for {file_path}")
                return False
    return True

def validate_configurations():
    """Validate key configuration files."""
    validations = [
        ("sudo visudo -cf /etc/sudoers.d/hootguard", "/etc/sudoers.d/hootguard"),
        ("lighttpd -t -f /etc/lighttpd/lighttpd.conf", "/etc/lighttpd/lighttpd.conf"),
    ]
    for cmd, config in validations:
        logging.info(f"Validating configuration: {config}")
        if not run_command(cmd):
            logging.error(f"Validation failed for {config}")
            return False
    return True

def restart_services():
    """Restart all relevant services."""
    services = ["hg-main.service", "pihole-FTL.service", "unbound.service"]
    for service in services:
        logging.info(f"Restarting {service}...")
        if not run_command(f"sudo systemctl restart {service}"):
            logging.error(f"Failed to restart {service}")
            return False
    return True

def cleanup_temp_files():
    """Clean up temporary files."""
    if os.path.exists(UPDATE_FLAG_FILE):
        try:
            os.remove(UPDATE_FLAG_FILE)
            logging.info(f"Removed temporary file: {UPDATE_FLAG_FILE}")
        except Exception as e:
            logging.error(f"Failed to remove temporary file {UPDATE_FLAG_FILE}: {e}")
            return False
    return True

def validate_update():
    """Validate that services are running after the update."""
    services = ["hg-main.service", "pihole-FTL.service"]
    for service in services:
        logging.info(f"Validating service: {service}")
        if not run_command(f"sudo systemctl is-active {service}"):
            logging.warning(f"{service} is not active. Please check manually.")
    return True

def main():
    """Main update process."""
    logging.info("Starting HootGuard update process...")

    if not create_backup():
        logging.error("Failed to create backups. Aborting update.")
        sys.exit(1)

    if not update_repository():
        logging.error("Failed to update the repository.")
        sys.exit(1)

    if not copy_files():
        logging.error("Failed to copy updated files.")
        sys.exit(1)

    if not apply_permissions():
        logging.error("Failed to apply correct permissions.")
        sys.exit(1)

    if not validate_configurations():
        logging.error("Failed to validate configurations.")
        sys.exit(1)

    if not restart_services():
        logging.error("Failed to restart services.")
        sys.exit(1)

    if not cleanup_temp_files():
        logging.warning("Failed to clean temporary files. Update process will continue.")

    if not validate_update():
        logging.warning("Post-update validation failed. Check services manually.")

    logging.info("HootGuard update completed successfully!")

if __name__ == "__main__":
    main()
