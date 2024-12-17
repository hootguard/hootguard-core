import os
import logging
import subprocess
import yaml

# Configuration
CONFIG_PATH = "/opt/hootguard/main/scripts/update/update_hootguard_config.yaml"
BACKUP_PATH = os.path.expanduser("~/backup")
ROLLBACK_FLAG_FILE = os.path.join(BACKUP_PATH, "rollback_pending")

# Logging configuration
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

def load_yaml_config(path):
    """Load configuration from YAML file."""
    with open(path, "r") as file:
        return yaml.safe_load(file)

def run_command(command):
    """Execute a shell command and handle errors."""
    try:
        subprocess.run(command, check=True, shell=True)
        logging.info(f"Successfully executed: {command}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing {command}: {e}")
        return False

def rollback_changes(config):
    """Rollback changes using the backup."""
    logging.warning("Initiating rollback...")
    for dest_name, src in config["backup_items"].items():
        backup_src = os.path.join(BACKUP_PATH, dest_name)
        if os.path.isdir(backup_src):
            logging.info(f"Restoring directory {src} from backup {backup_src}...")
            if not run_command(f"rsync -a {backup_src}/ {src}/"):
                logging.error(f"Failed to restore directory {src}")
                return False
        elif os.path.isfile(backup_src):
            logging.info(f"Restoring file {src} from backup {backup_src}...")
            if not run_command(f"cp {backup_src} {src}"):
                logging.error(f"Failed to restore file {src}")
                return False
        else:
            logging.warning(f"Backup for {src} not found. Skipping.")
    return True

def clear_rollback_flag():
    """Clear the rollback flag."""
    if os.path.exists(ROLLBACK_FLAG_FILE):
        os.remove(ROLLBACK_FLAG_FILE)
        logging.info("Rollback pending flag cleared.")

def main():
    """Main rollback process."""
    logging.info("Starting rollback process...")

    # Check if rollback is pending
    if not os.path.exists(ROLLBACK_FLAG_FILE):
        logging.info("No rollback required. Exiting.")
        return

    # Load configuration
    try:
        config = load_yaml_config(CONFIG_PATH)
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return

    # Perform rollback
    if rollback_changes(config):
        logging.info("Rollback completed successfully.")
        clear_rollback_flag()
    else:
        logging.error("Rollback failed. Manual intervention may be required.")

if __name__ == "__main__":
    main()
