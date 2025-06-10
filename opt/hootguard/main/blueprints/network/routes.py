from flask import Blueprint, render_template, request, redirect, session
import threading
from scripts.network_get_configuration import network_get_active_config
from scripts.network_save_configuration_and_reboot import network_save_config_and_reboot, network_save_config_and_reboot_v6

# Create the Network Blueprint
network_bp = Blueprint('network', __name__)

# Define the network routes within the Blueprint
@network_bp.route('/network_settings', methods=['GET', 'POST'])
def network_settings():
        network_config = network_get_active_config() # Call external function
        return render_template('network_settings.html', config=network_config)

# -------- NEW ROUTE - NETWORK V4 --------
@network_bp.route('/network_change', methods=['GET', 'POST'])
def network_change():
        session.pop('logged_in', None)  # Log out the user
        network_change_thread = threading.Thread(target=network_save_config_and_reboot, args=(request.form['ip_address'], request.form['subnet_mask'], request.form['standard_gateway'],))
        network_change_thread.start()
        return render_template('reboot/reboot_network.html')  # Render a page that will redirect the user

# -------- NEW ROUTE - NETWORK V6 --------
@network_bp.route('/network_change_v6', methods=['GET', 'POST'])
def network_change_v6():
        session.pop('logged_in', None)  # Log out the user
        network_change_v6_thread = threading.Thread(target=network_save_config_and_reboot_v6, args=(request.form['ip_address_v6'],))
        network_change_v6_thread.start()
        return render_template('reboot/reboot_network.html')  # Render a page that will redirect the user
