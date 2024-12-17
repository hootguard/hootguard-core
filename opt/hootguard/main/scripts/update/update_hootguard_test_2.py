import os
import subprocess
import sys
import logging
import yaml

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
#UPDATE_FLAG_FILE = config['update']['update_flag']
BACKUP_PATH = os.path.expanduser("/home/hootguard/backup")
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


def main():
    try:
        if not create_backup():
            logging.error("Failed to create backups. Aborting update.")
        if not update_repository():
            logging.error("Failed to update the repository.")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
