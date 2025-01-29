#!/bin/bash

# Set your Dynu username and IP Update Password (MD5 Hash)
HN="xxx"
PW="xxx"

# Get the current public IPv6 address
IPV6=$(curl -s -6 ifconfig.co)

# Update only IPv6
curl -s -k "https://api.dynu.com/nic/update?hostname=$HN&password=$PW&myipv6=$IPV6&myip=no" | curl -k -o /opt/hootguard/ddns/log/dynu.log -K -
