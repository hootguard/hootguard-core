#!/bin/bash
# Get current IPv6 address of eth0 interface
ipv6=$(ip -6 addr show dev eth0 scope global | grep inet6 | awk '{print $2}' | cut -d/ -f1)

# Print the IPv6 address of eth0
#echo "Current IPv6 address of eth0: $ipv6"

# Update DuckDNS with only the IPv6 address
echo url="https://www.duckdns.org/update?domains=xxxx&token=xxx&ipv6=$ipv6" | curl -k -o /opt/hootguard/ddns/log/duck.log -K -

