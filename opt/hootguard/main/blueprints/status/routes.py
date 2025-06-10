from flask import Blueprint, jsonify
from scripts.service_check_internet_connection import check_internet_connection
from scripts.service_check_adblocker_status import check_adblocker_status
from scripts.service_check_vpn_status import check_vpn_status
from scripts.service_check_ddns_status import check_ddns_status

# Create the Status Blueprint
status_bp = Blueprint('status', __name__)

# Define the status routes within the Blueprint
@status_bp.route('/status/internet', methods=['GET', 'POST'])
def internet_status():
    status = check_internet_connection() # Call external function
    return jsonify({'status': status})

# -------- NEW ROUTE - ADBLOCKER / PI-HOLE STATUS --------
@status_bp.route('/status/adblocker', methods=['GET', 'POST'])
def adblocker_status():
    status = check_adblocker_status() # Call external function
    return jsonify({'status': status})

# -------- NEW ROUTE - VPN / PI-VPN STATUS --------
@status_bp.route('/status/vpn', methods=['GET', 'POST'])
def vpn_status():
    status = check_vpn_status() # Call external function
    return jsonify({'status': status})

# -------- NEW ROUTE - DDNS STATUS --------
@status_bp.route('/status/ddns', methods=['GET', 'POST'])
def ddns_status():
    status = check_ddns_status() # Call external function
    return jsonify({'status': status})
