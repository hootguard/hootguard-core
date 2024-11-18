# Script Name: ddns_log_user_consent.py
# Version: 1.1
# Author: HootGuard
# Date: 22. April 2024

# Description:
# This script records the user's consent regarding sharing their public IP address with Cloudflare and HootGuard DDNS. It appends the consent information, including the consent statement, timestamp, and hostname, to the 'ddns_consent.txt' file.
# The script fetches the hostname using the socket module, creates a consent_info dictionary with relevant details, and appends it to the specified file path. Upon execution, it provides feedback indicating the process status.

# Update: 
# THIS SCRIPT IS CURRENTLY NOT IN USE


#import json
#from datetime import datetime
#import socket
#from .global_config import DDNS_CONSENT_FILE_PATH
#
#def ddns_record_consent():
#    """
#    Records the user's consent by appending it to the ddns_consent.txt file.
#    """
#    # Fetch the hostname
#    hostname = socket.gethostname()
#
#    # Consent information
#    consent_info = {
#        "consent_given": True,
#        "consent_statement": "I consent to share my public IP address with Cloudflare and HootGuard DDNS.",
#        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#        "hostname": hostname
#    }
#
#    # Append consent information to the file
#    file_path = DDNS_CONSENT_FILE_PATH  
#    with open(file_path, "a") as file:
#        file.write(json.dumps(consent_info) + "\n")
