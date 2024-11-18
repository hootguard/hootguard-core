import shutil
import subprocess
from cryptography.fernet import Fernet

from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
NW_DHCPCD_PATH = config['dhcp']['dhcpcd_path']
NW_DHCPCD_ORIGINAL_PATH = config['dhcp']['dhcpcd_original_path']
PW_HASHED_PASSWORD_PATH = config['passwords']['hashed_password_path']
PW_HASHED_DEFAULT_PASSWORD_PATH = config['passwords']['hashed_default_password_path']
PW_ENCRYPTED_PASSWORD_PATH = config['passwords']['encrypted_password_path']
PW_SECRET_KEY_PATH = config['passwords']['secret_key_path']

def reset_ip_and_password():
    if not reset_ip_address():
        logger.info("ERROR - Failed to reset the ip address")
    if not reset_passwords():
        logger.info("ERROR - Failed to reset web and pi-hole password")

    logger.info("IP address and password successfully reset")
    return True

def reset_ip_address():
    try:
        subprocess.run(['sudo', 'cp', NW_DHCPCD_ORIGINAL_PATH, NW_DHCPCD_PATH], check=True)
        logger.info("IP address reset to DHCP successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reset IP address: {e}")
        return False


def reset_passwords():
    try:
        # Reset web password
        shutil.copy(PW_HASHED_DEFAULT_PASSWORD_PATH, PW_HASHED_PASSWORD_PATH)
        logger.info("INFO - Web password reset successfully.")

        # Reset Pi-hole password
        with open(PW_ENCRYPTED_PASSWORD_PATH, 'rb') as file:
            encrypted_password = file.read()
        with open(PW_SECRET_KEY_PATH, 'rb') as file:
            key = file.read()

        # Decrypt the password
        fernet = Fernet(key)
        decrypted_password = fernet.decrypt(encrypted_password).decode()

        # Run the pihole command and capture both stdout and stderr
        result = subprocess.run(
            ['pihole', '-a', '-p', decrypted_password], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )

        # Combine stdout and stderr for easier checking
        combined_output = result.stdout + result.stderr

        # Check if the word 'error' or any similar error message is present
        if "error" in combined_output.lower():
            logger.info(f"ERROR - Failed to reset Pi-hole password: {combined_output}")
            return False
        else:
            logger.info(f"SUCCESS - Pi-hole password reset successfully. Output: {combined_output}")
            return True

    except Exception as e:
        logger.info(f"ERROR - Failed to reset passwords: {e}")
        return False
