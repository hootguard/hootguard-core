from cryptography.fernet import Fernet
import traceback

key_path = '/opt/hootguard/password/secret.key'
encrypted_path = '/opt/hootguard/password/encrypted_password.txt'

try:
    with open(key_path, 'rb') as key_file:
        key = key_file.read()

    with open(encrypted_path, 'rb') as encrypted_file:
        encrypted_password = encrypted_file.read()

    fernet = Fernet(key)
    decrypted_password = fernet.decrypt(encrypted_password).decode()
    print(f"Decrypted password: {decrypted_password}")

except Exception as e:
    print("Decryption failed")
    print("Error message:", e)
    print("Traceback:")
    print(traceback.format_exc())
