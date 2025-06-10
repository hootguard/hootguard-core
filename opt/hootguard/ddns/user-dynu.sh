#!/bin/bash

# Set your Dynu username and IP Update Password (MD5 Hash)
HN="xxx"
PW="xxx"

# Get the current public IPv4 and IPv6 addresses
IPV4=$(curl -s -4 ifconfig.co)

# Update only IPv4
echo url="https://api.dynu.com/nic/update?hostname=$HN&password=$PW&myip=$IPV4&myipv6=no" | curl -k -o /opt/hootguard/ddns/log/dynu.log -K -
