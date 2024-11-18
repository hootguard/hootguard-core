import os
import subprocess
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Define the path where WireGuard configuration files are stored
WG_CONF_DIRECTORY = config['vpn']['wireguard_main_path']

def generate_wireguard_keys(interface_name):
    """Generates private and public keys for the specified interface and saves them in /etc/wireguard/."""
    
    # Define file paths for the private and public keys
    private_key_file = os.path.join(WG_CONF_DIRECTORY, f"privatekey_{interface_name}")
    public_key_file = os.path.join(WG_CONF_DIRECTORY, f"publickey_{interface_name}")
    
    private_key = None
    public_key = None

    try:
        # Generate the private key
        private_key = subprocess.check_output(['wg', 'genkey']).strip()
        
        # Save the private key to a file
        with open(private_key_file, 'wb') as pk_file:
            pk_file.write(private_key)
        
        # Generate the public key using the private key
        public_key = subprocess.check_output(['wg', 'pubkey'], input=private_key)
        
        # Save the public key to a file
        with open(public_key_file, 'wb') as pub_file:
            pub_file.write(public_key)

        # Set the ownership to root:wireguard for both keys
        subprocess.check_call(['sudo', 'chown', 'root:root', private_key_file])
        subprocess.check_call(['sudo', 'chown', 'root:wireguard', public_key_file])

        # Set the permissions to 770 for both keys
        subprocess.check_call(['sudo', 'chmod', '600', private_key_file])
        subprocess.check_call(['sudo', 'chmod', '770', public_key_file])

        logger.debug(f"Private and public keys generated and saved for interface {interface_name}")
        return private_key.decode()  # Return the private key as a string for further use
    except Exception as e:
        logger.debug(f"Error generating keys for interface {interface_name}: {e}")
        return None
    finally:
        # Ensure private and public key variables are cleared from memory
        private_key = None
        public_key = None
        logger.debug(f"Private and public key variables cleared for interface {interface_name}")

#if __name__ == "__main__":
#    # Example usage
#    interface_name = "wg0"  # Replace with the desired interface name
#    generate_wireguard_keys(interface_name)
