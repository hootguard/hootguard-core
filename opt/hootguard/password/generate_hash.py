# Version:      1.1
# Date:         21 Jan 2024
# Author:       HootGuard
# Description:  This file will generate a random passwort of 6 characters long.
#                               This password will be used to login into the settings page (login)
#                               and to login into the pi-hole dashboard (admin).
#                               This file also creates a hash of this password and stores it in a
#                               file (hashed_password.txt) where the flask app (settings.py) takes
#                               out the hash to compare it with the entered password in the login.
#
# Verion update: Since the reset button will not only reset the static ip address to dhcp, it will also
#                reset the passwort to a default password. Therefore in this change, we create two files
#               the file hased_password.txt and the file hased_password.txt.default. In case of the reset
#               button is used, hased_password.txt.default will overwrite the hased_password.txt file and so
#               set the password back to the default vale.
#

import random
import string
import subprocess
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet

# Function to write and read key for encryption/decryption
def load_or_create_key():
    try:
        with open("secret.key", "rb") as key_file:
            return key_file.read()
    except FileNotFoundError:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
        return key

def encrypt_password(password, key):
    """
    Encrypt the password.
    """
    f = Fernet(key)
    return f.encrypt(password.encode())

def decrypt_password(encrypted_password, key):
    """
    Decrypt the password.
    """
    f = Fernet(key)
    return f.decrypt(encrypted_password).decode()

def generate_random_password(length):
    """
    Generate a random password with a specified length.
    """
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choices(characters, k=length))

def set_pihole_password(password):
    """
    Set the password for the Pi-hole admin dashboard.
    """
    command = f"sudo pihole -a -p {password}"
    subprocess.run(command, shell=True)

def generate_hash_and_save_to_file():
    """
    Generate a random password, print it, hash it, encrypt it, and save the hash and the encrypted password to files.
    """
    #password = generate_random_password(6)  # 6 characters long
    password = "HootGuardSentry"  # Standard Password
    # print(f"Generated Password: {password}")

    # Set the password for Pi-hole
    set_pihole_password(password)

    hashed_password = generate_password_hash(password)
    # print(f"Hashed Password: {hashed_password}")

    # Encrypt the password
    key = load_or_create_key()
    encrypted_password = encrypt_password(password, key)

    # Write the hash to the active password file
    with open("hashed_password.txt", "w") as file:
        file.write(hashed_password)

    # Write the hash to the default password file
    with open("hashed_password.txt.default", "w") as file:
        file.write(hashed_password)

    # Write the encrypted password to a file
    with open("encrypted_password.txt", "wb") as file:
        file.write(encrypted_password)

# Call this function to generate and hash the password and save the hash to a file
generate_hash_and_save_to_file()
