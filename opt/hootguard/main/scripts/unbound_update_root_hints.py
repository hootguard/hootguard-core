import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename='/var/log/hootguard_system.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')

def update_root_hints():
    # Check if today is the first day of the month
    if datetime.now().day == 1:
        try:
            # Command to update the root.hints file
            command = "wget https://www.internic.net/domain/named.root -qO- | sudo tee /var/lib/unbound/root.hints"
            subprocess.run(command, shell=True, check=True)
            logging.info("root.hints updated successfully.")
        except subprocess.CalledProcessError as e:
            logging.error("An error occurred while updating root.hints:", e)
    else:
        logging.info("No roots.hints update required today.")

# Run the update function once and exit
update_root_hints()
