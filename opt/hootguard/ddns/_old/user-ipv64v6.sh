#!/bin/bash

# Set your Key and Domain. Domain only for read configuration script
KEY="xxx"
DOMAIN="xxx"

# Set your update URL
UPDATE_URL="https://ipv64.net/nic/update?key=$KEY"

# Run the curl command
curl -sSL "$UPDATE_URL"

# Check if the curl command was successful
if [ $? -eq 0 ]; then
    echo "$(date): IPv64 update successful."
else
    echo "$(date): IPv64 update failed." >&2
fi
