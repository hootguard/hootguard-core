hootguard@HGSentry3:/opt/hootguard/main/scripts/update $ more update_hootguard.py
# Script Name: update_hootguard.py
# Version: 0.6
# Author: HootGuard
# Date: 5. January 2025

# Description:
# This script automates the simplified update process for the HootGuard system by performing the following steps:
# 1. Creates a tarball backup of critical system paths to facilitate rollback if needed.
# 2. Clones or pulls the HootGuard Git repository into a temporary directory to fetch the latest updates.
# 3. Uses rsync to synchronize new files from the repository to the corresponding system directories.
# 4. Applies appropriate permissions and ownership to ensure proper access control.
# 5. Reboots the system to finalize the changes.
#
# The script includes robust logging, error handling, and shell command execution for a reliable update process.

import os
import subprocess
import sys
import logging
import shlex

# ------------------------------------------------------------------------------
# CONFIGURATION SECTION - adapt paths / repos / services to your environment
# ------------------------------------------------------------------------------

BACKUP_TARBALL_PATH = "/home/hootguard/backup/hootguard_backup.tar.gz"
# Directories that we want to back up in one go (tar):
CRITICAL_PATHS = [
    "/opt/hootguard",
    "/var/www/html/hootguard",
    "/etc/unbound/unbound.conf.d",
    "/etc/pihole/setupVars.conf",
    "/var/www/html/index.html",
    "/etc/lighttpd/lighttpd.conf",
    "/etc/systemd/system/hg-deactivate-i2c.service",
    "/etc/systemd/system/hg-info-display.service",
    "/etc/systemd/system/hg-main.service",
    "/etc/systemd/system/hg-ntp-update.service",
    "/etc/systemd/system/hg-reset.service",
    "/etc/systemd/system/hg-snooze.service",
    "/etc/resolvconf.conf",
    "/boot/config.txt",
    "/usr/local/bin/hootguard",
    #"/etc/dhcpcd.conf.bkp",
    #"/etc/dhcpcd.conf.original",
    #"/etc/hostname",
    #"/etc/hosts",
]

# Path to clone or pull the repository:
LOCAL_REPO_PATH = "/tmp/hootguard_update"

# The GitHub repo containing the latest HootGuard code:
REPO_URL = "https://github.com/hootguard/hootguard-core.git"

# The top-level directories inside the cloned repo that map to your system dirs.
# We simply keep it minimal here. You can expand if your repo has more structure.
# Key = local repo subdirectory, Value = system directory to receive updates
REPO_TO_SYSTEM_MAP = {
    "opt/hootguard": "/opt/hootguard",
    "var/www/html/hootguard": "/var/www/html/hootguard",
    "etc/unbound/unbound.conf.d": "/etc/unbound/unbound.conf.d",
    "etc/pihole/setupVars.conf": "/etc/pihole/setupVars.conf",
    "var/www/html/index.html": "/var/www/html/index.html",
    "etc/lighttpd/lighttpd.conf": "/etc/lighttpd/lighttpd.conf",
    "etc/systemd/system/hg-deactivate-i2c.service": "/etc/systemd/system/hg-deactivate-i2c.service",
    "etc/systemd/system/hg-info-display.service": "/etc/systemd/system/hg-info-display.service",
    "etc/systemd/system/hg-main.service": "/etc/systemd/system/hg-main.service",
    "etc/systemd/system/hg-ntp-update.service": "/etc/systemd/system/hg-ntp-update.service",
    "etc/systemd/system/hg-reset.service": "/etc/systemd/system/hg-reset.service",
    "etc/systemd/system/hg-snooze.service": "/etc/systemd/system/hg-snooze.service",
    "etc/resolvconf.conf": "/etc/resolvconf.conf",
    "boot/config.txt": "/boot/config.txt",
    "usr/local/bin/hootguard": "/usr/local/bin/hootguard",
    #"etc/dhcpcd.conf.bkp": "/etc/dhcpcd.conf.bkp",
    #"etc/dhcpcd.conf.original": "/etc/dhcpcd.conf.original",
    #"etc/hostname": "/etc/hostname",
    #"etc/hosts": "/etc/hosts"
}

# Optional: A list of chmod or chown commands to ensure correct permissions
# after the update. Example structure: (command, path).
# In practice, you might read this from a config, or keep it inline here.
PERMISSIONS_COMMANDS = [
#    ("chmod 0644" "/opt/hootguard"),
#    ("chown hootguard:hootguard", "/opt/hootguard"),
#    ("chmod 0644", "/opt/hootguard/adblock"),
#    ("chown hootguard:hootguard", "/opt/hootguard/adblock"),
#    ("chmod 0644", "/opt/hootguard/ddns"),
#    ("chown hootguard:hootguard", "/opt/hootguard/ddns"),
#    ("chmod 0644", "/opt/hootguard/display"),
#    ("chown hootguard:hootguard", "/opt/hootguard/display"),
#    ("chmod 0644", "/opt/hootguard/main"),
#    ("chown hootguard:hootguard", "/opt/hootguard/main"),
#    ("chmod 0644", "/opt/hootguard/misc"),
#    ("chown hootguard:hootguard", "/opt/hootguard/misc"),
#    ("chmod 0644", "/opt/hootguard/password"),
#    ("chown hootguard:hootguard", "/opt/hootguard/password"),
#    ("chmod 0644", "/opt/hootguard/snooze"),
#    ("chown hootguard:hootguard", "/opt/hootguard/snooze"),
#    ("chmod 0644", "/opt/hootguard/vpn"),
#    ("chown hootguard:hootguard", "/opt/hootguard/vpn"),

    ("find /opt/hootguard -type d -exec chmod 0755 {} +", ""),  # Apply 0755 to all directories
    ("find /opt/hootguard -type f -exec chmod 0644 {} +", ""),  # Apply 0644 to all files
    ("chown -R hootguard:hootguard /opt/hootguard", "")         # Recursively set ownership

    ("chmod 0644", "/etc/lighttpd/lighttpd.conf"),
    ("chown root:root", "/etc/lighttpd/lighttpd.conf"),

    ("chmod 0755", "/boot/config.txt"),
    ("chown root:root", "/boot/config.txt"),

    ("chmod 0644", "/etc/pihole/setupVars.conf"),
    ("chown root:root", "/etc/pihole/setupVars.conf"),

    ("chmod 0644", "/etc/sudoers.d/hootguard"),
    ("chown root:root", "/etc/sudoers.d/hootguard"),

    ("chmod 0644", "/etc/systemd/system/hg-deactivate-i2c.service"),
    ("chown root:root", "/etc/systemd/system/hg-deactivate-i2c.service"),

    ("chmod 0644", "/etc/systemd/system/hg-info-display.service"),
    ("chown root:root", "/etc/systemd/system/hg-info-display.service"),

    ("chmod 0644", "/etc/systemd/system/hg-main.service"),
    ("chown root:root", "/etc/systemd/system/hg-main.service"),

    ("chmod 0644", "/etc/systemd/system/hg-ntp-update.service"),
    ("chown root:root", "/etc/systemd/system/hg-ntp-update.service"),

    ("chmod 0644", "/etc/systemd/system/hg-reset.service"),
    ("chown root:root", "/etc/systemd/system/hg-reset.service"),

    ("chmod 0644", "/etc/systemd/system/hg-snooze.service"),
    ("chown root:root", "/etc/systemd/system/hg-snooze.service"),

    ("chmod 0644", "/etc/unbound/unbound.conf.d/pi-hole.conf"),
    ("chown root:root", "/etc/unbound/unbound.conf.d/pi-hole.conf"),

    ("chmod 0644", "/etc/resolvconf.conf]"),
    ("chown root:root", "/etc/resolvconf.conf]"),

    ("chmod 0700", "/usr/local/bin/hootguard"),
    ("chown root:root", "/usr/local/bin/hootguard"),

#    ("chmod 0644", "/etc/dhcpcd.conf.bkp"),
#    ("chown root:root", "/etc/dhcpcd.conf.bkp"),

#    ("chmod 0644", "/etc/dhcpcd.conf.original"),
#    ("chown root:root", "/etc/dhcpcd.conf.original"),

#    ("chmod 0644", "/etc/hostname"),
#    ("chown root:root", "/etc/hostname"),

#    ("chmod 0644", "/etc/hosts"),
#    ("chown root:root", "/etc/hosts"),
]

# ------------------------------------------------------------------------------
# LOGGING SETUP - logs both to console and /var/log/hootguard_system.log (example)
# ------------------------------------------------------------------------------

LOG_FILENAME = "/var/log/hootguard_system.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(filename)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILENAME),
        logging.StreamHandler(sys.stdout)
    ]
)

# ------------------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------------------

def run_shell_command(command):
    """
    Runs a shell command (string), logs success/error, and returns (True/False).
    Example: run_shell_command("tar -czf backup.tar.gz /etc/lighttpd")
    """
    logging.info(f"Running command: {command}")
    try:
        # Using shlex.split for safer handling of spaces, but direct string can work if well-formed
        subprocess.run(shlex.split(command), check=True)
        logging.info(f"Command succeeded: {command}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed ({e.returncode}): {e.cmd}")
        return False

def create_backup_tar():
    """
    Creates a tar.gz backup of CRITICAL_PATHS and stores it in BACKUP_TARBALL_PATH.
    If the tar creation fails, return False. Otherwise True.
    """
    # Ensure the parent directory of the tarball exists
    backup_dir = os.path.dirname(BACKUP_TARBALL_PATH)
    os.makedirs(backup_dir, exist_ok=True)

    # Build the tar command
    # --exclude='__pycache__' as an example, add more excludes as needed.
    # Using 'zcf' -> z = gzip, c = create, f = filename
    paths_str = " ".join(CRITICAL_PATHS)
    #command = f"tar -zcf {BACKUP_TARBALL_PATH} --exclude='__pycache__' {paths_str}"
    command = (
        f"tar -zcf {BACKUP_TARBALL_PATH} "
        f"--exclude='__pycache__' "
        f"--exclude='/var/www/html/admin' "  # <--- Exclude admin folder here
        f"{paths_str}"
    )

    logging.info(f"Creating backup tarball at: {BACKUP_TARBALL_PATH}")
    return run_shell_command(command)

def clone_or_pull_repo():
    """
    Clones the repo into LOCAL_REPO_PATH if it doesn't exist.
    If it does exist, attempts a 'git pull'. Return True on success, False otherwise.
    """
    if os.path.isdir(LOCAL_REPO_PATH):
        logging.info("Local repo path exists, pulling changes...")
        command = f"git -C {LOCAL_REPO_PATH} pull"
    else:
        logging.info("Cloning the repo for the first time...")
        command = f"git clone {REPO_URL} {LOCAL_REPO_PATH}"

    return run_shell_command(command)

def apply_new_files():
    """
    RSync new files from the local cloned repo to the system directories or files.
    Loops over REPO_TO_SYSTEM_MAP. Return True on full success, False on any error.
    """
    for local_subpath, system_dest in REPO_TO_SYSTEM_MAP.items():
        repo_path = os.path.join(LOCAL_REPO_PATH, local_subpath)  # e.g. /tmp/hootguard_update/etc/hostname

        if not os.path.exists(repo_path):
            logging.warning(f"Repo subpath not found, skipping: {repo_path}")
            continue

        # Check if the repo path is a directory or a file.
        if os.path.isdir(repo_path):
            # Directory => add trailing slash to both sides
            command = f"rsync -a {repo_path}/ {system_dest}/"
            logging.info(f"Syncing directory {repo_path}/ -> {system_dest}/ ...")
        elif os.path.isfile(repo_path):
            # File => no trailing slash on the source
            # Destination could be a directory or a file path
            if os.path.isdir(system_dest):
                # If system_dest is a directory, place the file inside it
                command = f"rsync -a {repo_path} {system_dest}/"
                logging.info(f"Syncing file {repo_path} -> directory {system_dest}/ ...")
            else:
                # If system_dest is the exact file path
                command = f"rsync -a {repo_path} {system_dest}"
                logging.info(f"Syncing file {repo_path} -> file {system_dest} ...")
        else:
            logging.warning(f"Path {repo_path} is neither file nor directory, skipping.")
            continue

        if not run_shell_command(command):
            logging.error(f"Failed to rsync from {repo_path} to {system_dest}")
            return False

    return True

def apply_permissions():
    """
    Applies predefined chmod/chown commands from PERMISSIONS_COMMANDS.
    Return True if all succeed, False if any fail.
    """
    for (cmd, path) in PERMISSIONS_COMMANDS:
        if os.path.exists(path):
            full_cmd = f"{cmd} {path}"
            logging.info(f"Applying: {full_cmd}")
            if not run_shell_command(full_cmd):
                return False
        else:
            logging.warning(f"Path not found for permission update: {path}")
    return True

def reboot():
    """
    Reboots the system.
    """
    logging.info("Rebooting the system now...")
    # Make sure you REALLY want to do this automatically.
    run_shell_command("reboot")

# ------------------------------------------------------------------------------
# MAIN FLOW
# ------------------------------------------------------------------------------

def main():
    """
    Main update flow:
    1. Create a tar backup of critical paths.
    2. Clone or pull the new repository code.
    3. Rsync new files to the system.
    4. Apply permissions.
    5. Reboot.
    """
    logging.info("=== Starting HootGuard Simplified Update Process ===")

    # Step 1: Backup
    logging.info("STEP 1: Backup critical paths.")
    if not create_backup_tar():
        logging.error("Backup failed! Aborting update.")
        sys.exit(1)

    # Step 2: Clone or Pull Repo
    logging.info("STEP 2: Retrieve latest HootGuard code from GitHub.")
    if not clone_or_pull_repo():
        logging.error("Repo retrieval failed! Aborting update.")
        sys.exit(1)

    # Step 3: Apply new files from repo
    logging.info("STEP 3: RSync new files onto the system.")
    if not apply_new_files():
        logging.error("File sync failed! Aborting update.")
        # Optional: Could do a rollback here by untarring backup if you want.
        sys.exit(1)

    # Step 4: Apply permissions
    logging.info("STEP 4: Apply required permissions.")
    if not apply_permissions():
        logging.warning("Some permission commands failed. Check logs.")
        # You could decide to abort or continue. We'll just continue for now.

    # Step 5: Reboot
    logging.info("STEP 5: Reboot system to finalize changes.")
    reboot()


if __name__ == "__main__":
    main()
