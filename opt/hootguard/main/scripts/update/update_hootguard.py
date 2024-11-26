import os
import subprocess
import sys

REPO_URL = "https://github.com/hootguard/hootguard-core.git"
LOCAL_REPO_PATH = "/tmp/hootguard_update"
CURRENT_PATHS = {
    "etc": "/etc",
    "opt_hootguard": "/opt/hootguard",
    "var_www_html": "/var/www/html"
}

def run_command(command):
    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing {command}: {e}")
        return False

def update_repository():
    if os.path.exists(LOCAL_REPO_PATH):
        print("Pulling latest changes from repository...")
        return run_command(f"git -C {LOCAL_REPO_PATH} pull")
    else:
        print("Cloning repository for the first time...")
        return run_command(f"git clone {REPO_URL} {LOCAL_REPO_PATH}")

def copy_files():
    for folder, dest in CURRENT_PATHS.items():
        source_path = os.path.join(LOCAL_REPO_PATH, folder)
        if os.path.exists(source_path):
            print(f"Updating {dest} from {source_path}...")
            if not run_command(f"rsync -a {source_path}/ {dest}/"):
                return False
    return True

def restart_services():
    print("Restarting Flask application...")
    return run_command("sudo systemctl restart hg-main.service")

def main():
    print("Starting HootGuard update process...")
    #if not update_repository():
    #    print("Failed to update the repository.")
    #    sys.exit(1)

    #if not copy_files():
    #    print("Failed to copy updated files.")
    #    sys.exit(1)

    #if not restart_services():
    #    print("Failed to restart services.")
    #    sys.exit(1)

    #print("HootGuard update completed successfully!")

if __name__ == "__main__":
    main()
