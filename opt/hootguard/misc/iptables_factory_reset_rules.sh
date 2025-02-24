#!/bin/bash

# Flush existing IPv4 rules (ensure a clean state)
iptables -F
iptables -t nat -F
iptables -t mangle -F

# Set default policies to block all traffic
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback traffic (localhost)
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established and related incoming traffic
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow mDNS (Multicast DNS) on UDP 5353
iptables -A INPUT -p udp --dport 5353 -j ACCEPT

# Allow incoming HTTP traffic (port 80)
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# Allow incoming SSH traffic (port 22)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Log dropped packets for troubleshooting (optional)
iptables -A INPUT -j LOG --log-prefix "Dropped INPUT: "
iptables -A FORWARD -j LOG --log-prefix "Dropped FORWARD: "

# Save the updated rules
iptables-save > /etc/iptables/rules.v4

# IPv6 rules

# Flush existing IPv6 rules (ensure a clean state)
ip6tables -F
ip6tables -t nat -F
ip6tables -t mangle -F

# Set default policies for IPv6 to block all traffic
ip6tables -P INPUT DROP
ip6tables -P FORWARD DROP
ip6tables -P OUTPUT ACCEPT

# Allow loopback traffic for IPv6
ip6tables -A INPUT -i lo -j ACCEPT
ip6tables -A OUTPUT -o lo -j ACCEPT

# Allow established and related incoming IPv6 traffic
ip6tables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow mDNS (Multicast DNS) on UDP 5353
ip6tables -A INPUT -p udp --dport 5353 -j ACCEPT

# Allow incoming HTTP traffic (port 80) for IPv6
ip6tables -A INPUT -p tcp --dport 80 -j ACCEPT

# Log dropped packets for IPv6 (optional)
ip6tables -A INPUT -j LOG --log-prefix "Dropped INPUT (IPv6): "
ip6tables -A FORWARD -j LOG --log-prefix "Dropped FORWARD (IPv6): "

# Save the updated IPv6 rules
ip6tables-save > /etc/iptables/rules.v6

echo "Iptables rules have been set to allow only port 80 and block all other traffic."
