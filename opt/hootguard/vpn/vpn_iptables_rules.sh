#!/bin/bash

# Source the Python script to load configuration
eval $(/usr/bin/python3 /opt/hootguard/main/scripts/firewall_load_iptables_global_config.py)

# Display variable values for verification
#echo "ETH_INTERFACE_1: $ETH_INTERFACE_1"
#echo "ETH_INTERFACE_1_NETWORK: $ETH_INTERFACE_1_NETWORK"
#echo "WG_INTERFACE_1: $WG_INTERFACE_1"
#echo "WG_INTERFACE_2: $WG_INTERFACE_2"
#echo "IPV4_ADDRESS_WG_INT_1: $IPV4_ADDRESS_WG_INT_1"
#echo "IPV4_NETWORK_WG_INT_1: $IPV4_NETWORK_WG_INT_1"
#echo "IPV4_ADDRESS_WG_INT_2: $IPV4_ADDRESS_WG_INT_2"
#echo "IPV4_NETWORK_WG_INT_2: $IPV4_NETWORK_WG_INT_2"
#echo "IPV6_NETWORK_WG_INT_1: $IPV6_NETWORK_WG_INT_1"
#echo "IPV6_NETWORK_WG_INT_2: $IPV6_NETWORK_WG_INT_2"
#echo "PIHOLE_IP: $PIHOLE_IP"

# Flush existing rules
iptables -F
iptables -t nat -F
iptables -t mangle -F

# Set default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow mDNS traffic (UDP port 5353)
iptables -A INPUT -i $ETH_INTERFACE_1 -p udp --dport 5353 -j ACCEPT
ip6tables -A INPUT -i $ETH_INTERFACE_1 -p udp --dport 5353 -j ACCEPT

# Allow IGMP traffic for multicast
iptables -A INPUT -i $ETH_INTERFACE_1 -p igmp -j ACCEPT

# Allow VPN traffic
iptables -A INPUT -p udp --dport 51820 -j ACCEPT
iptables -A INPUT -p udp --dport 51821 -j ACCEPT

# Allow DNS traffic from the local network to the HootGuard Sentry
iptables -A INPUT -i $ETH_INTERFACE_1 -s $ETH_INTERFACE_1_NETWORK -p udp --dport 53 -j ACCEPT
iptables -A INPUT -i $ETH_INTERFACE_1 -s $ETH_INTERFACE_1_NETWORK -p tcp --dport 53 -j ACCEPT

# Block traffic between VPN clients
iptables -A FORWARD -i $WG_INTERFACE_1 -o $WG_INTERFACE_1 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -o $WG_INTERFACE_2 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -o $WG_INTERFACE_1 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -o $WG_INTERFACE_2 -j DROP

# Block access from VPN clients to the VPN server's addresses (both FORWARD and INPUT chains)
# Forward chain
#iptables -A FORWARD -i $WG_INTERFACE_1 -d $IPV4_ADDRESS_WG_INT_1 -j DROP
#iptables -A FORWARD -i $WG_INTERFACE_1 -d $IPV4_ADDRESS_WG_INT_2 -j DROP
#iptables -A FORWARD -i $WG_INTERFACE_2 -d $IPV4_ADDRESS_WG_INT_1 -j DROP
#iptables -A FORWARD -i $WG_INTERFACE_2 -d $IPV4_ADDRESS_WG_INT_2 -j DROP

# Input chain
iptables -A INPUT -i $WG_INTERFACE_1 -d $IPV4_ADDRESS_WG_INT_1 -j DROP
iptables -A INPUT -i $WG_INTERFACE_1 -d $IPV4_ADDRESS_WG_INT_2 -j DROP
iptables -A INPUT -i $WG_INTERFACE_2 -d $IPV4_ADDRESS_WG_INT_1 -j DROP
iptables -A INPUT -i $WG_INTERFACE_2 -d $IPV4_ADDRESS_WG_INT_2 -j DROP

# Allow SSH (rate limited to prevent brute-force attacks)
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m limit --limit 3/min --limit-burst 5 -j ACCEPT

# Allow HTTP
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# DNS Rules: Allow only Pi-hole and block all other DNS requests
# Allow DNS traffic from VPN clients to Pi-hole (FORWARD chain)
iptables -A FORWARD -i $WG_INTERFACE_1 -p udp --dport 53 -d $PIHOLE_IP -j ACCEPT
iptables -A FORWARD -i $WG_INTERFACE_1 -p tcp --dport 53 -d $PIHOLE_IP -j ACCEPT
iptables -A FORWARD -i $WG_INTERFACE_2 -p udp --dport 53 -d $PIHOLE_IP -j ACCEPT
iptables -A FORWARD -i $WG_INTERFACE_2 -p tcp --dport 53 -d $PIHOLE_IP -j ACCEPT

# Allow DNS traffic from VPN clients to Pi-hole (INPUT chain)
iptables -A INPUT -i $WG_INTERFACE_1 -p udp --dport 53 -d $PIHOLE_IP -j ACCEPT
iptables -A INPUT -i $WG_INTERFACE_1 -p tcp --dport 53 -d $PIHOLE_IP -j ACCEPT
iptables -A INPUT -i $WG_INTERFACE_2 -p udp --dport 53 -d $PIHOLE_IP -j ACCEPT
iptables -A INPUT -i $WG_INTERFACE_2 -p tcp --dport 53 -d $PIHOLE_IP -j ACCEPT

# Drop all other DNS requests from VPN clients
iptables -A FORWARD -i $WG_INTERFACE_1 -p udp --dport 53 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -p tcp --dport 53 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -p udp --dport 53 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -p tcp --dport 53 -j DROP

# Block DNS over TLS (DoT)
iptables -A FORWARD -i $WG_INTERFACE_1 -p tcp --dport 853 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -p tcp --dport 853 -j DROP

# Block common DoH and external DNS IPs
iptables -A FORWARD -i $WG_INTERFACE_1 -d 1.1.1.1 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -d 1.0.0.1 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -d 8.8.8.8 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -d 8.8.4.4 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -d 9.9.9.9 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -d 149.112.112.112 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -d 208.67.222.222 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -d 208.67.220.220 -j DROP

iptables -A FORWARD -i $WG_INTERFACE_2 -d 1.1.1.1 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -d 1.0.0.1 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -d 8.8.8.8 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -d 8.8.4.4 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -d 9.9.9.9 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -d 149.112.112.112 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -d 208.67.222.222 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -d 208.67.220.220 -j DROP

# Block DoH (DNS over HTTPS)
iptables -A FORWARD -i $WG_INTERFACE_1 -p tcp -d 1.1.1.1 --dport 443 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -p tcp -d 8.8.8.8 --dport 443 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_1 -p tcp -d 9.9.9.9 --dport 443 -j DROP

iptables -A FORWARD -i $WG_INTERFACE_2 -p tcp -d 1.1.1.1 --dport 443 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -p tcp -d 8.8.8.8 --dport 443 -j DROP
iptables -A FORWARD -i $WG_INTERFACE_2 -p tcp -d 9.9.9.9 --dport 443 -j DROP

# Allow VPN clients to access the internet
iptables -A FORWARD -i $WG_INTERFACE_1 -o $ETH_INTERFACE_1 -j ACCEPT
iptables -A FORWARD -i $WG_INTERFACE_2 -o $ETH_INTERFACE_1 -j ACCEPT
iptables -A FORWARD -i $ETH_INTERFACE_1 -o $WG_INTERFACE_1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $ETH_INTERFACE_1 -o $WG_INTERFACE_2 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT

# Enable NAT for VPN clients
iptables -t nat -A POSTROUTING -s $IPV4_NETWORK_WG_INT_1 -o $ETH_INTERFACE_1 -j MASQUERADE
iptables -t nat -A POSTROUTING -s $IPV4_NETWORK_WG_INT_2 -o $ETH_INTERFACE_1 -j MASQUERADE

# Enable NAT for local network
iptables -t nat -A POSTROUTING -s $ETH_INTERFACE_1_NETWORK -o $ETH_INTERFACE_1 -j MASQUERADE

# Log dropped packets for troubleshooting (optional)
iptables -A INPUT -j LOG --log-prefix "Dropped INPUT: "
iptables -A FORWARD -j LOG --log-prefix "Dropped FORWARD: "

# Save rules
iptables-save > /etc/iptables/rules.v4

# IPv6 rules
ip6tables -F
ip6tables -t nat -F
ip6tables -t mangle -F
ip6tables -P INPUT ACCEPT
ip6tables -P FORWARD DROP
ip6tables -P OUTPUT ACCEPT
ip6tables -A INPUT -i lo -j ACCEPT
ip6tables -A OUTPUT -o lo -j ACCEPT
ip6tables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
ip6tables -A INPUT -p udp --dport 51820 -j ACCEPT
ip6tables -A INPUT -p tcp --dport 22 -j ACCEPT
ip6tables -A INPUT -p tcp --dport 80 -j ACCEPT
ip6tables -A FORWARD -i $WG_INTERFACE_1 -o $WG_INTERFACE_1 -j DROP
ip6tables -A FORWARD -i $WG_INTERFACE_2 -o $WG_INTERFACE_2 -j DROP
ip6tables -A FORWARD -i $WG_INTERFACE_1 -o $ETH_INTERFACE_1 -j ACCEPT
ip6tables -A FORWARD -i $WG_INTERFACE_2 -o $ETH_INTERFACE_1 -j ACCEPT
ip6tables -A FORWARD -i $ETH_INTERFACE_1 -o $WG_INTERFACE_1 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
ip6tables -A FORWARD -i $ETH_INTERFACE_1 -o $WG_INTERFACE_2 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
ip6tables -t nat -A POSTROUTING -s $IPV6_NETWORK_WG_INT_1 -o $ETH_INTERFACE_1 -j MASQUERADE
ip6tables -t nat -A POSTROUTING -s $IPV6_NETWORK_WG_INT_2 -o $ETH_INTERFACE_1 -j MASQUERADE

# Log dropped packets for IPv6 (optional)
ip6tables -A INPUT -j LOG --log-prefix "Dropped INPUT (IPv6): "
ip6tables -A FORWARD -j LOG --log-prefix "Dropped FORWARD (IPv6): "

# Save IPv6 rules
ip6tables-save > /etc/iptables/rules.v6
