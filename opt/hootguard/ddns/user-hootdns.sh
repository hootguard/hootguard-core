#!/bin/bash

# Path to the global configuration file
CONFIG_PATH="/opt/hootguard/misc/global_config.yaml"

# Function to get a value from the YAML file using yq
get_config_value() {
    /usr/local/bin/yq e ".$1" "$CONFIG_PATH"
}

# Retrieve API key and subdomain from the configuration file
API_KEY=$(get_config_value "ddns.user_hootdns_api_key")
SUBDOMAIN=$(get_config_value "ddns.user_hootdns_subdomain")

#echo "$API_KEY"
#echo "$SUBDOMAIN"

# Check if API key and subdomain are set
if [ -z "$API_KEY" ] || [ -z "$SUBDOMAIN" ]; then
    echo "$(date): API key or subdomain not set in configuration." >&2
    exit 1
fi

# Dynamically get your public IPv4 address
IPV4=$(curl -s https://api.ipify.org)

# Verify that the public IP address was successfully retrieved
if [ -z "$IPV4" ]; then
    echo "$(date): Failed to retrieve public IPv4 address." >&2
    exit 1
fi

# Set your update URL
UPDATE_URL="http://hootdns.com:5053/ddns/update"

# Run the curl command to update IPv4
response=$(curl -sSL -X POST "$UPDATE_URL" -d "subdomain=$SUBDOMAIN" -d "api_key=$API_KEY" -d "ipv4=$IPV4" -d "ipv6=")

# Check if the update was successful
if echo "$response" | grep -q '"status":"updated"'; then
    echo "$(date): HootDNS IPv4 update successful."
else
    echo "$(date): HootDNS IPv4 update failed: $response" >&2
fi
