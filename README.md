# HootGuard: Your All-in-One Privacy and Security Solution

HootGuard is an all-in-one VPN, DNS, and network security solution designed specifically for Raspberry Pi devices. It combines Pi-hole, Unbound, and WireGuard to provide an easy-to-use, secure, and customizable setup. HootGuard offers advanced features such as temporary and unlimited VPN client configurations, bandwidth and time-limited VPN options, and a centralized web interface for managing your network.

---

## Features

- **VPN Management**: Supports multiple WireGuard interfaces (`wg0`, `wg1`) for unlimited and temporary VPN clients.
- **Integrated DNS**: Utilizes Pi-hole for ad blocking and Unbound for DNS security.
- **User-Friendly Interface**: Web-based interface built with Flask, offering detailed settings and status pages.
- **Customizable**: Full control over VPN client keys, IP configurations, and DNS settings via YAML files.
- **Security**: Separation of server and client keys, advanced logging, and secure key storage.

---

## Current Status

This is a **beta version** currently under testing. Once testing is completed, the beta version will be available for download as a preconfigured SD card image from [hootguard.com](https://hootguard.com), where detailed documentation will also be provided.

HootGuard is actively working on a version optimized for Raspberry Pi 3B+. We are currently working on a Version for Raspberry Pi 4 (coming soon).

---

## Installation and Usage

HootGuard is designed for advanced users comfortable with managing a Raspberry Pi. To get started:
1. Flash the HootGuard image (coming soon) onto an SD card.
2. Insert the SD card into your Raspberry Pi and boot it up.
3. Access the HootGuard web interface to configure your setup.

Detailed installation instructions and documentation will be available at [hootguard.com](https://hootguard.com).

---

## Directory Structure

HootGuard's repository is organized as follows:
- ***/etc/*** # Configuration files and system-level settings
- ***/opt/hootguard/*** # Core components of HootGuard
- - ├── main/ # Main scripts and Flask application
    - └── blueprints/ # Blueprints for the flask application
    - └── scripts/ # Python scripts for managing VPN, DNS, and system
    - └── static/ # Static files for the web interface (e.g., images, QR codes)
    - └── templates/ # HTML templates for the Flask application
  - ├── adblock/ # Adblock active profile status
  - ├── ddns/ # DDNS profiles and profile status
  - ├── display/ # Optional display management
  - ├── password/ # Password management
  - ├── snooze/ # Snooze time and status managment
  - ├── misc/ # Miscellaneous files (e.g., version tracking, flags)
- ***/var/www/html/*** # Web interface and navigation files 
- ***README.md*** # Project overview and usage instructions
