#!/bin/bash

# Set your HootDNS subdomain and API key
SUBDOMAIN="your_subdomain_here"
API_KEY="your_api_key_here"

# Dynamically get your public IPv4 and IPv6 addresses
IPV4=$(curl -s https://api.ipify.org)
IPV6=$(curl -s -6 ifconfig.co)

# Verify that the public IP addresses were successfully retrieved
if [ -z "$IPV4" ] && [ -z "$IPV6" ]; then
    echo "$(date): Failed to retrieve any public IP address." >&2
    exit 1
fi

# Set your update URL
UPDATE_URL="http://hootdns.com:5053/ddns/update"

# Construct curl command with available IPs
if [ -n "$IPV4" ] && [ -n "$IPV6" ]; then
    response=$(curl -sSL -X POST "$UPDATE_URL" -d "subdomain=$SUBDOMAIN" -d "api_key=$API_KEY" -d "ipv4=$IPV4" -d "ipv6=$IPV6")
elif [ -n "$IPV4" ]; then
    response=$(curl -sSL -X POST "$UPDATE_URL" -d "subdomain=$SUBDOMAIN" -d "api_key=$API_KEY" -d "ipv4=$IPV4")
elif [ -n "$IPV6" ]; then
    response=$(curl -sSL -X POST "$UPDATE_URL" -d "subdomain=$SUBDOMAIN" -d "api_key=$API_KEY" -d "ipv6=$IPV6")
fi

# Check if the update was successful
if echo "$response" | grep -q '"status":"updated"'; then
    echo "$(date): HootDNS update successful."
else
    echo "$(date): HootDNS update failed: $response" >&2
fi
