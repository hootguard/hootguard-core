#!/bin/bash

# Set your Key and Domain. Domain only for read configuration script
KEY="xxx"
DOMAIN="xxx"

# Dynamically get your public IPv4 address
IPV4=$(curl -s https://api.ipify.org)

# Verify that the public IP address was successfully retrieved
if [ -z "$IPV4" ]; then
    echo "$(date): Failed to retrieve public IPv4 address." >&2
    exit 1
fi

# Set your update URL
UPDATE_URL="https://ipv64.net/nic/update?key=$KEY&ip=$IPV4"

# Run the curl command
curl -sSL "$UPDATE_URL"

# Check if the curl command was successful
if [ $? -eq 0 ]; then
    echo "$(date): IPv64 update successful."
else
    echo "$(date): IPv64 update failed." >&2
fi
