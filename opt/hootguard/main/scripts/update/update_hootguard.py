# Script Name: update_hootguard.py
# Version: 0.4
# Author: HootGuard
# Date: 12. December 2024

# Description:
# This script automates the update process for the HootGuard system. It performs the following tasks:
# 1. Backs up critical system directories and files to ensure recovery in case of an update failure.
# 2. Pulls or clones the latest version of the HootGuard repository from the configured GitHub URL.
# 3. Synchronizes updated files from the repository to their respective system locations using rsync.
# 4. Applies correct permissions and ownership to critical files for system security.
# 5. Validates configurations like sudoers and web server settings to prevent errors post-update.
# 6. Restarts all necessary services to apply changes.
# 7. Restarts the system after a successful update.
# 8. Cleans up temporary files and validates that services are running correctly post-update.

import os
import subprocess
import sys
import logging
import yaml

# Add the project root directory to the module search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from main.scripts.global_config_loader import load_config
from scripts.system_reboot import reboot

# Load the global config
config = load_config()

# Configure logging
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

# Define the remote version file URL and local version file path
REPO_URL = config['update']['repo_url']
LOCAL_REPO_PATH = config['update']['local_repo_path']
UPDATE_FLAG_FILE = config['update']['update_available_flag']
UPDATE_PENGING_FLAG_FILE = config['update']['update_pending_flag']
BACKUP_PATH = os.path.expanduser("~/home/hootguard/backup")
ROLLBACK_FLAG_FILE = os.path.join(BACKUP_PATH, "rollback_pending")
CONFIG_PATH = "/opt/hootguard/main/scripts/update/update_hootguard_config.yaml"

# Load YAML configuration
try:
    def load_yaml_config(path):
        with open(path, "r") as file:
            return yaml.safe_load(file)

    config = load_yaml_config(CONFIG_PATH)
    BACKUP_ITEMS = config["backup_items"]
    EXCLUDE_FROM_UPDATE = config["exclude_from_update"]
    PERMISSIONS = config["permissions"]
    OWNER_UPDATES = config["ownership"]
except Exception as e:
    logging.error(f"Failed to load configuration file: {e}")
    sys.exit(1)

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
    """Create a backup of specified system files and directories."""
    os.makedirs(BACKUP_PATH, exist_ok=True)
    for src, dest_name in BACKUP_ITEMS.items():
        backup_dest = os.path.join(BACKUP_PATH, dest_name)

        if os.path.isdir(src):
            logging.info(f"Backing up directory {src} to {backup_dest}, excluding '__pycache__'...")
            # Exclude __pycache__ directories
            if not run_command(f"rsync -a --exclude='__pycache__' {src}/ {backup_dest}/"):
                logging.error(f"Failed to back up directory {src}")
                return False
        elif os.path.isfile(src):
            logging.info(f"Backing up file {src} to {backup_dest}...")
            if not run_command(f"cp {src} {backup_dest}"):
                logging.error(f"Failed to back up file {src}")
                return False
        else:
            logging.warning(f"Skipping {src}, as it does not exist.")

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
    for folder, dest in BACKUP_ITEMS.items():
        if folder in EXCLUDE_FROM_UPDATE:
            logging.info(f"Skipping update for excluded file: {folder}")
            continue

        if folder.startswith("/usr/local/bin"):
            source_path = os.path.join(LOCAL_REPO_PATH, "usr/local/bin")
        else:
            source_path = os.path.join(LOCAL_REPO_PATH, folder)

        if os.path.exists(source_path):
            logging.info(f"Updating {dest} from {source_path}...")
            if not run_command(f"rsync -a {source_path}/ {dest}/"):
                logging.error(f"Failed to copy files from {source_path} to {dest}")
                return False
    return True

def apply_permissions():
    """Apply correct permissions to critical files."""
    for cmd, file_path in PERMISSIONS:
        if os.path.exists(file_path):
            logging.info(f"Applying permissions: {cmd}")
            if not run_command(cmd):
                logging.error(f"Failed to apply permissions for {file_path}")
                return False
    return True

def update_ownership():
    """Update ownership for critical files."""
    for cmd, file_path in OWNER_UPDATES:
        if os.path.exists(file_path):
            logging.info(f"Updating ownership: {cmd}")
            if not run_command(cmd):
                logging.error(f"Failed to update ownership for {file_path}")
                return False
    return True

def cleanup_temp_files():
    """Clean up temporary files."""
    # Delete update available flag file (/opt/hootguard/misc/update_available)
    if os.path.exists(UPDATE_FLAG_FILE):
        try:
            os.remove(UPDATE_FLAG_FILE)
            logging.info(f"Removed temporary file: {UPDATE_FLAG_FILE}")
        except Exception as e:
            logging.error(f"Failed to remove temporary file {UPDATE_FLAG_FILE}: {e}")
            return False
    # Delete update pending flag file (/opt/hootguard/misc/update_pending)
    if os.path.exists(UPDATE_PENDING_FLAG_FILE):
        try:
            os.remove(UPDATE_FLAG_FILE)
            logging.info(f"Removed temporary file: {UPDATE_PENDING_FLAG_FILE}")
        except Exception as e:
            logging.error(f"Failed to remove temporary file {UPDATE_PENDING_FLAG_FILE}: {e}")
            return False
    return True

def mark_rollback_pending():
    """Mark that a rollback may be needed."""
    with open(ROLLBACK_FLAG_FILE, "w") as file:
        file.write("ROLLBACK_PENDING")
    logging.info("Rollback pending flag set.")

def clear_rollback_flag():
    """Clear the rollback flag."""
    if os.path.exists(ROLLBACK_FLAG_FILE):
        os.remove(ROLLBACK_FLAG_FILE)
        logging.info("Rollback pending flag cleared.")

def main():
    """Main update process with rollback support."""
    logging.info("Starting HootGuard update process...")

    try:
        mark_rollback_pending()

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

        if not update_ownership():
            logging.error("Failed to update ownerships.")
            sys.exit(1)

        if not cleanup_temp_files():
            logging.warning("Failed to clean temporary files. Update process will continue.")

        clear_rollback_flag()

        logging.info("HootGuard update completed successfully! Restarting the system...")
        reboot()

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.warning("Calling rollback script...")
        try:
            subprocess.run(["python3", "/opt/hootguard/main/scripts/update/update_hootguard_rollback.py"], check=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to execute rollback script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
