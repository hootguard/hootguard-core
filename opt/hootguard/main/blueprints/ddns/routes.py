from flask import Blueprint, request, render_template, redirect, url_for
from scripts.ddns_read_status import ddns_read_status_and_return_status
from scripts.ddns_read_configuration_duckdns import ddns_read_config_duckdns
from scripts.ddns_read_configuration_ipv64 import ddns_read_config_ipv64
from scripts.ddns_read_configuration_dynu import ddns_read_config_dynu
from scripts.ddns_read_configuration_cloudflare import ddns_read_config_cloudflare
from scripts.ddns_update_status_file import ddns_update_status
from scripts.ddns_change_crontab import ddns_update_crontab
from scripts.ddns_configure_user_cloudflare import ddns_write_and_activate_cloudflare
from scripts.ddns_configure_user_duckdns import ddns_write_and_activate_duckdns
from scripts.ddns_configure_user_ipv64 import ddns_write_and_activate_ipv64
from scripts.ddns_configure_user_dynu import ddns_write_and_activate_dynu
from scripts.ddns_update_endpoint_in_global_config import replace_vpn_endpoint
from scripts.global_logger import logger

# Create the DDNS Blueprint
ddns_bp = Blueprint('ddns', __name__)

# Define the DDNS routes within the Blueprint
@ddns_bp.route('/ddns_settings', methods=['GET', 'POST'])
def ddns_settings():
        status_message = ddns_read_status_and_return_status()
        nds = request.args.get('nds')
        return render_template('ddns/ddns_settings.html', status_message=status_message, new_ddns_set=nds)


@ddns_bp.route('/ddns_activate_hootguard_cloudflare', methods=['GET', 'POST'])
def ddns_activate_hootguard_cloudflare():
        try:
            # Update DDNS status
            ddns_update_status('hootguard-cloudflare')
            # Update crontab
            ddns_update_crontab('hootguard-cloudflare')

            # If all operations are successful, render the settings page
            return redirect('/ddns_settings?nds=True')
        except Exception as e:
            logger.info(e)
            # If an error occurs, redirect to the error route
            return redirect(url_for('error'))


# ------------------------------------------------------------------------------------------
# --------------------------------- CLOUDFLARE ---------------------------------------------
# ------------------------------------------------------------------------------------------

@ddns_bp.route('/ddns_settings_user_cloudflare', methods=['GET', 'POST'])
def ddns_settings_user_cloudflare():
    # Call the ddns_read_config_cloudflare function to get auth_email, auth_key, zone_identifier, and record_name
    auth_email, auth_key, zone_identifier, record_name, auth_email_ipv6, auth_key_ipv6, zone_identifier_ipv6, record_name_ipv6 = ddns_read_config_cloudflare()

    # Helper function to mask and shorten sensitive data
    def mask_and_shorten_data(data, max_length=15):
        if data and len(data) > 4:  # Check if data is not empty and longer than 4 characters
            visible_suffix = data[-4:]  # Keep the last 4 characters visible
            mask_length = max_length - len(visible_suffix)  # Calculate how many characters to mask
            masked = '*' * mask_length + visible_suffix  # Combine masking and visible characters
            return masked
        return data  # Return original data if empty or shorter than 4 characters

    # Mask and shorten sensitive fields
    auth_key = mask_and_shorten_data(auth_key)
    zone_identifier = mask_and_shorten_data(zone_identifier)
    auth_key_ipv6 = mask_and_shorten_data(auth_key_ipv6)
    zone_identifier_ipv6 = mask_and_shorten_data(zone_identifier_ipv6)

    # Replace empty strings with None for optional fields
    auth_email = auth_email or None
    record_name = record_name or None
    auth_email_ipv6 = auth_email_ipv6 or None
    record_name_ipv6 = record_name_ipv6 or None

    # Render the template with the masked and shortened data
    return render_template(
        'ddns/ddns_settings_user_cloudflare.html',
        current_auth_email=auth_email,
        current_auth_key=auth_key,
        current_zone_identifier=zone_identifier,
        current_record_name=record_name,
        current_auth_email_ipv6=auth_email_ipv6,
        current_auth_key_ipv6=auth_key_ipv6,
        current_zone_identifier_ipv6=zone_identifier_ipv6,
        current_record_name_ipv6=record_name_ipv6
    )



@ddns_bp.route('/ddns_activate_user_cloudflare_ipv6', methods=['GET', 'POST'])
def ddns_activate_user_cloudflare_ipv6():
    try:
        # Update Cloudflare configuration file
        ddns_write_and_activate_cloudflare(request.form['e_mail_ipv6'], request.form['auth_key_ipv6'], request.form['zone_identifier_ipv6'], request.form['record_name_ipv6'], "ipv6")
        # Update DDNS status
        ddns_update_status('user-cloudflare-ipv6')
        # Update crontab
        ddns_update_crontab('user-cloudflare-ipv6')
        # Update Endpoint in global configuratio file
        replace_vpn_endpoint(request.form['record_name_ipv6'])

        # If all operations are successful, render the settings page
        return redirect('/ddns_settings?nds=True')
    except Exception as e:
        logger.info(e)
        # If an error occurs, redirect to the error route
        return redirect(url_for('error'))


@ddns_bp.route('/ddns_activate_user_cloudflare_ipv4', methods=['GET', 'POST'])
def ddns_activate_user_cloudflare_ipv4():
    try:
        # Update Cloudflare configuration file
        ddns_write_and_activate_cloudflare(request.form['e_mail'], request.form['auth_key'], request.form['zone_identifier'], request.form['record_name'], "ipv4")
        # Update DDNS status
        ddns_update_status('user-cloudflare-ipv4')
        # Update crontab
        ddns_update_crontab('user-cloudflare-ipv4')
        # Update Endpoint in global configuratio file
        replace_vpn_endpoint(request.form['record_name'])


        # If all operations are successful, render the settings page
        return redirect('/ddns_settings?nds=True')
    except Exception as e:
        logger.info(e)
        # If an error occurs, redirect to the error route
        return redirect(url_for('error'))


# ------------------------------------------------------------------------------------------
# --------------------------------- IPV64 --------------------------------------------------
# ------------------------------------------------------------------------------------------

@ddns_bp.route('/ddns_settings_user_ipv64', methods=['GET', 'POST'])
def ddns_settings_user_ipv64():

    # Call the ddns_read_config_ipv64 function to get the key
    ipv4_domain, ipv4_key, ipv6_domain, ipv6_key = ddns_read_config_ipv64()

    # Helper function to mask and shorten sensitive data
    def mask_and_shorten_data(data, max_length=15):
        if data and len(data) > 4:  # Check if data is not empty and longer than 4 characters
            visible_suffix = data[-4:]  # Keep the last 4 characters visible
            mask_length = max_length - len(visible_suffix)  # Calculate how many characters to mask
            masked = '*' * mask_length + visible_suffix  # Combine masking and visible characters
            return masked
        return data  # Return original data if empty or shorter than 4 characters

    # Mask and shorten token fields
    ipv4_key = mask_and_shorten_data(ipv4_key)
    ipv6_key = mask_and_shorten_data(ipv6_key)

    # Render the template with the masked and shortened tokens
    return render_template(
        'ddns/ddns_settings_user_ipv64.html',
        current_ipv4_domain=ipv4_domain,
        current_ipv4_key=ipv4_key,
        current_ipv6_domain=ipv6_domain,
        current_ipv6_key=ipv6_key
    )

@ddns_bp.route('/ddns_activate_user_ipv64_ipv6', methods=['GET', 'POST'])
def ddns_activate_user_ipv64_ipv6():
        try:
            # Update IPv64 configuration file
            ddns_write_and_activate_ipv64(request.form['domain-ipv6'], request.form['token-ipv6'], "ipv6")
            # Update DDNS status
            ddns_update_status('user-ipv64-ipv6')
            # Update crontab
            ddns_update_crontab('user-ipv64-ipv6')
	    # Update Endpoint in global configuratio file
            replace_vpn_endpoint(request.form['domain-ipv6'])

            # If all operations are successful, render the settings page
            #return redirect(url_for('ddns_settings'))
            return redirect('/ddns_settings?nds=True')
        except Exception as e:
            logger.info(e)
            # If an error occurs, redirect to the error route
            return redirect(url_for('error'))

@ddns_bp.route('/ddns_activate_user_ipv64_ipv4', methods=['GET', 'POST'])
def ddns_activate_user_ipv64_ipv4():
        try:
            # Update IPv64 configuration file
            ddns_write_and_activate_ipv64(request.form['domain'], request.form['token'], "ipv4")
            # Update DDNS status
            ddns_update_status('user-ipv64-ipv4')
            # Update crontab
            ddns_update_crontab('user-ipv64-ipv4')
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
# --------------------------------- DYNU --------------------------------------------------
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
# ------------------------------- DUCKDNS --------------------------------------------------
# ------------------------------------------------------------------------------------------

@ddns_bp.route('/ddns_settings_user_duckdns', methods=['GET', 'POST'])
def dns_settings_user_duckdns():
    # Call the ddns_read_config_duckdns function to get domain and token
    domain, token, ipv6_domain, ipv6_token = ddns_read_config_duckdns()

    # Helper function to mask and shorten sensitive data
    def mask_and_shorten_data(data, max_length=15):
        if data and len(data) > 4:  # Check if data is not empty and longer than 4 characters
            visible_suffix = data[-4:]  # Keep the last 4 characters visible
            mask_length = max_length - len(visible_suffix)  # Calculate how many characters to mask
            masked = '*' * mask_length + visible_suffix  # Combine masking and visible characters
            return masked
        return data  # Return original data if empty or shorter than 4 characters

    # Mask and shorten token fields
    token = mask_and_shorten_data(token)
    ipv6_token = mask_and_shorten_data(ipv6_token)

    # Render the template with the masked and shortened tokens
    return render_template(
        'ddns/ddns_settings_user_duckdns.html',
        current_domain=domain,
        current_token=token,
        current_domain_ipv6=ipv6_domain,
        current_token_ipv6=ipv6_token
    )


@ddns_bp.route('/ddns_activate_user_duckdns_ipv6', methods=['GET', 'POST'])
def ddns_activate_user_duckdns_ipv6():
        try:
            # Update DuckDNS configuration file
            ddns_write_and_activate_duckdns(request.form['domain-ipv6'], request.form['token-ipv6'], "ipv6")
            # Update DDNS status
            ddns_update_status('user-duckdns-ipv6')
            # Update crontab
            ddns_update_crontab('user-duckdns-ipv6')
	    # Update Endpoint in global configuratio file
            replace_vpn_endpoint(request.form['domain-ipv6'])

            # If all operations are successful, render the settings page
            #return redirect(url_for('ddns_settings'))
            return redirect('/ddns_settings?nds=True')
        except Exception as e:
            logger.info(e)
            # If an error occurs, redirect to the error route
            return redirect(url_for('error'))


@ddns_bp.route('/ddns_activate_user_duckdns_ipv4', methods=['GET', 'POST'])
def ddns_activate_user_duckdns_ipv4():
        try:
            # Update DuckDNS configuration file
            ddns_write_and_activate_duckdns(request.form['domain'], request.form['token'], "ipv4")
            # Update DDNS status
            ddns_update_status('user-duckdns-ipv4')
            # Update crontab
            ddns_update_crontab('user-duckdns-ipv4')
	    # Update Endpoint in global configuratio file
            replace_vpn_endpoint(request.form['domain'])


            # If all operations are successful, render the settings page
            #return redirect(url_for('ddns_settings'))
            return redirect('/ddns_settings?nds=True')
        except Exception as e:
            logger.info(e)
            # If an error occurs, redirect to the error route
            return redirect(url_for('error'))


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
