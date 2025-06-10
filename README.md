# HootGuard

**Simplify and enhance your home network security, privacy, and ad-blocking—all with an intuitive web interface.**

[![License](https://img.shields.io/badge/License-See%20LICENSE-blue.svg)](./LICENSE)
[![Built with Python](https://img.shields.io/badge/Built%20with-Python%203.x-blue.svg)](#)
![Status](https://img.shields.io/badge/Status-Release%20Candidate-green.svg)](#)

## Overview

HootGuard is an open-source solution designed to effortlessly protect your home network and improve your online privacy. Combining multiple tools—such as Pi-hole for ad-blocking, WireGuard for secure VPN access, and Unbound for DNS privacy—HootGuard provides a streamlined and user-friendly interface that makes advanced network security accessible to everyone.

**Key Capabilities:**
- **Ad-Blocking (Pi-hole):** Reduce unwanted ads, malicious websites, and trackers with customizable, pre-defined blocking profiles.
- **VPN Services (WireGuard):** Easily set up secure VPN connections for remote access, including temporary and bandwidth-limited VPN users.
- **Privacy-Oriented DNS (Unbound):** Enhance your privacy and security with DNS over TLS and DNSSEC validation.
- **Dynamic DNS (DDNS) Integration:** Seamlessly configure DuckDNS or Cloudflare for reliable domain name resolution.
- **Intuitive Web Interface:** Manage it all—user accounts, VPN clients, DNS filtering, and security settings—from a simple, modern dashboard.

## Who Is It For?

HootGuard is ideal for anyone looking to:
- Protect their home network from ads, tracking, and malicious content.
- Securely access their home network remotely via VPN without complex setup steps.
- Safeguard their family’s internet experience by blocking adult content, gambling, or specific social media sites.
- Enhance overall privacy and reduce unnecessary traffic through robust DNS protections.

Whether you’re privacy-conscious, security-focused, or just want a cleaner internet experience at home, HootGuard provides a comprehensive and user-friendly solution.

## Technology Stack

- **Backend:** Python (Flask), Bash scripts
- **Frontend:** HTML, CSS
- **Networking Tools:** Pi-hole, WireGuard, Unbound

## Installation

**Requirements:**
- A Raspberry Pi (currently verified on Raspberry Pi 3B; Pi 4 support is in progress).
- An SD Card with at least 8GB capacity (32GB recommended).

**Steps:**
1. **Download the Image:**  
   Visit [HootGuard.com](https://hootguard.com) to download the latest HootGuard image.
   
2. **Write Image to SD Card:**  
   Use a tool like [Rapsberry Pi Imager](https://www.raspberrypi.com/software/) to flash the image to your SD card.
   
3. **Boot Up the Raspberry Pi:**  
   Insert the SD card into your Raspberry Pi and connect it to your network router.
   
4. **Initial Setup:**  
   Power on the Raspberry Pi and wait for it to obtain a network address. You can then access the HootGuard web interface from your browser using the Pi’s IP address.

## Configuration & Setup

**Network Configuration:**
- Assign a static IPv4 (and ideally a static IPv6) address to the Raspberry Pi running HootGuard.
- Configure your router’s firewall to allow traffic as needed for VPN connections.
- Set your router’s DNS server to HootGuard for network-wide ad-blocking and filtering.

**VPN & DDNS:**
- Choose a DDNS provider: Dynu or HootDNS (HootGuards own DNS service) are supported.  
- To use HootDNS you need to buy our software from [Hootguard.com](https://hootguard.com/).
- Enter the DDNS credentials into HootGuard’s web interface.
- Create VPN users, scan their generated QR codes, and start using the VPN immediately.

**Additional Requirements:**
- Users may need to add port forwarding rules on their router for remote VPN access.
- HootGuard can automatically manage and update DNS records if properly configured with your DDNS provider.

## Usage

Once installed and configured, visit the HootGuard web interface (http://hootguard.local) to:

- **Manage Ad-Blocking:**  
  Select from pre-defined profiles (e.g., block adult websites, gambling, social media) and fine-tune the level of filtering.
  
- **Create VPN Clients:**  
  Set up permanent or temporary VPN users, scan their QR codes with a mobile WireGuard client, and enjoy secure remote access.
  
- **Monitor Network Status:**  
  View logs, statistics, and performance metrics from the dashboard.
  
- **Update Settings on the Fly:**  
  Adjust DNS configurations, change ad-block filters, and modify user access without needing to SSH into the device.

## Documentation & Resources

Official documentation is in progress. For the latest instructions, tutorials, and video guides, please check:

- [HootGuard Official Website](https://hootguard.com)
- [YouTube Channel](https://www.youtube.com/@HootGuard)

Feel free to submit issues and feature requests through GitHub’s [Issues](./issues) tab.

## License

HootGuard is open-source software. For details, please see the [LICENSE](./LICENSE) file.

---

**Contributions & Feedback:**  
We welcome contributions—whether bug reports, feature requests, or pull requests. Join our community and help make HootGuard even better!

**Contact:**  
For inquiries, reach out via our website’s contact form or open a GitHub issue.
