import yaml
import time
from flask import Blueprint, request, render_template, redirect, url_for
from scripts.ddns_read_status import ddns_read_status_and_return_status
from scripts.ddns_read_configuration_dynu import ddns_read_config_dynu
from scripts.ddns_update_status_file import ddns_update_status
from scripts.ddns_change_crontab import ddns_update_crontab
from scripts.ddns_configure_user_hootdns import ddns_activate_hootdns
from scripts.ddns_configure_user_dynu import ddns_write_and_activate_dynu
from scripts.ddns_update_endpoint_in_global_config import replace_vpn_endpoint
from scripts.ddns_update_hootdns_global_config import ddns_update_hootdns_credentials
# --- OTHER SCRIPTS ---
from scripts.global_logger import logger
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Path to the global configuration file
# CONFIG_PATH = "/opt/hootguard/misc/global_config.yaml"

# Create the DDNS Blueprint
ddns_bp = Blueprint('ddns', __name__)

# HOOTDNS - Check if hootdns subdomain and api key are in global config
def check_hootdns_config():
    try:
        config = load_config() # Load the function file before checking
        sub = config['ddns']['user_hootdns_subdomain']
        key = config['ddns']['user_hootdns_api_key']
        if sub and key:
            return 'yes'
    except KeyError:
        pass
    return 'no'

# Get the full subdomain from global_config to set correct endpoint for VPN
def get_hootdns_full_subdomain():
    try:
        # Load the global config
        config = load_config()
        
        # Access the domain and subdomain values
        domain = config['ddns'].get('user_hootdns_domain', 'hootdns.com')
        subdomain = config['ddns'].get('user_hootdns_subdomain', '')

        if not subdomain:
            raise ValueError("Subdomain not set in configuration.")

        full_subdomain = f"{subdomain}.{domain}"
        return full_subdomain
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

# Define the DDNS routes within the Blueprint
@ddns_bp.route('/ddns_settings', methods=['GET', 'POST'])
def ddns_settings():
        status_message = ddns_read_status_and_return_status()
        nds = request.args.get('nds')
        hootdns = check_hootdns_config()
        return render_template('ddns/ddns_settings.html', status_message=status_message, new_ddns_set=nds, hootdns=hootdns)


# ------------------------------------------------------------------------------------------
# ----------------------------------- HOOTDNS ----------------------------------------------
# ------------------------------------------------------------------------------------------

@ddns_bp.route('/ddns_activate_user_hootdns_ipv6', methods=['GET', 'POST'])
def ddns_activate_user_hootdns_ipv6():
    # Optional: Write subdomain and API key to global_config.yaml
    subdomain = request.form.get('hootdns_subdomain')
    api_key = request.form.get('hootdns_api_key')
    print(subdomain)
    print(api_key)

    if subdomain and api_key:
        if ddns_update_hootdns_credentials(subdomain, api_key):
            time.sleep(0.2) # slight delay to ensure file write completes
            config = load_config() # force reload config

    try:
        # Activate HootDNS DDNS Service
        ddns_activate_hootdns("ipv6")
        # Update DDNS status
        ddns_update_status('user-hootdns-ipv6')
        # Update crontab
        ddns_update_crontab('user-hootdns-ipv6')

        # Get the full subdomain and update the endpoint
        full_subdomain = get_hootdns_full_subdomain()
        if full_subdomain:
            # Update Endpoint in global configuration file
            replace_vpn_endpoint(full_subdomain)

        # If all operations are successful, render the settings page
        #return redirect(url_for('ddns_settings'))
        return redirect('/ddns_settings?nds=True')
    except Exception as e:
        logger.info(e)
        # If an error occurs, redirect to the error route
        return redirect(url_for('error'))

@ddns_bp.route('/ddns_activate_user_hootdns_ipv4', methods=['GET', 'POST'])
def ddns_activate_user_hootdns_ipv4():
    try:
        # Activate HootDNS DDNS Service
        ddns_activate_hootdns("ipv4")
        # Update DDNS status
        ddns_update_status('user-hootdns-ipv4')
        # Update crontab
        ddns_update_crontab('user-hootdns-ipv4')
        # Get the full subdomain and update the endpoint
        full_subdomain = get_hootdns_full_subdomain()
        if full_subdomain:
            # Update Endpoint in global configuration file
            replace_vpn_endpoint(full_subdomain)

        # If all operations are successful, render the settings page
        #return redirect(url_for('ddns_settings'))
        return redirect('/ddns_settings?nds=True')
    except Exception as e:
        logger.info(e)
        # If an error occurs, redirect to the error route
        return redirect(url_for('error'))



# ------------------------------------------------------------------------------------------
# --------------------------------- DYNU ---------------------------------------------------
# ------------------------------------------------------------------------------------------

@ddns_bp.route('/ddns_settings_user_dynu', methods=['GET', 'POST'])
def ddns_settings_user_dynu():

    # Call the ddns_read_config_dynu function to get the key
    ipv4_domain, ipv4_password, ipv6_domain, ipv6_password = ddns_read_config_dynu()

    # Helper function to mask and shorten sensitive data
    def mask_and_shorten_data(data, max_length=15):
        if data and len(data) > 4:  # Check if data is not empty and longer than 4 characters
            visible_suffix = data[-4:]  # Keep the last 4 characters visible
            mask_length = max_length - len(visible_suffix)  # Calculate how many characters to mask
            masked = '*' * mask_length + visible_suffix  # Combine masking and visible characters
            return masked
        return data  # Return original data if empty or shorter than 4 characters

    # Mask and shorten token fields
    ipv4_password = mask_and_shorten_data(ipv4_password)
    ipv6_password = mask_and_shorten_data(ipv6_password)

    # Render the template with the masked and shortened tokens
    return render_template(
        'ddns/ddns_settings_user_dynu.html',
        current_ipv4_domain=ipv4_domain,
        current_ipv4_password=ipv4_password,
        current_ipv6_domain=ipv6_domain,
        current_ipv6_password=ipv6_password
    )

@ddns_bp.route('/ddns_activate_user_dynu_ipv6', methods=['GET', 'POST'])
def ddns_activate_user_dynu_ipv6():
        try:
            # Update DYNU configuration file
            ddns_write_and_activate_dynu(request.form['domain-ipv6'], request.form['password-ipv6'], "ipv6")
            # Update DDNS status
            ddns_update_status('user-dynu-ipv6')
            # Update crontab
            ddns_update_crontab('user-dynu-ipv6')
	    # Update Endpoint in global configuratio file
            replace_vpn_endpoint(request.form['domain-ipv6'])

            # If all operations are successful, render the settings page
            #return redirect(url_for('ddns_settings'))
            return redirect('/ddns_settings?nds=True')
        except Exception as e:
            logger.info(e)
            # If an error occurs, redirect to the error route
            return redirect(url_for('error'))

@ddns_bp.route('/ddns_activate_user_dynu_ipv4', methods=['GET', 'POST'])
def ddns_activate_user_dynu_ipv4():
        try:
            # Update DYNU configuration file
            ddns_write_and_activate_dynu(request.form['domain'], request.form['password'], "ipv4")
            # Update DDNS status
            ddns_update_status('user-dynu-ipv4')
            # Update crontab
            ddns_update_crontab('user-dynu-ipv4')
	    # Update Endpoint in global configuratio file
            replace_vpn_endpoint(request.form['domain'])

            # If all operations are successful, render the settings page
            #return redirect(url_for('ddns_settings'))
            return redirect('/ddns_settings?nds=True')
        except Exception as e:
            logger.info(e)
            # If an error occurs, redirect to the error route
            return redirect(url_for('error'))


# ------------------------------------------------------------------------------------------
# ---------------------------- DEACTIVATE DDNS ---------------------------------------------
# ------------------------------------------------------------------------------------------

@ddns_bp.route('/ddns_deactivate', methods=['GET', 'POST'])
def ddns_deactivate():
        try:
            # Update DDNS status
            ddns_update_status('no-config')
            # Update crontab - REMOVE CRONTAB
            ddns_update_crontab('no-config')

            # If all operations are successful, render the settings page
            #return redirect(url_for('ddns_settings'))
            return redirect('/ddns_settings?nds=True')
        except Exception as e:
            logger.info(e)
            # If an error occurs, redirect to the error route
            return redirect(url_for('error'))
