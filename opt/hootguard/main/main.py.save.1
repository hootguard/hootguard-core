# Standard library imports
import os
import threading
import subprocess
import time

# Third-party imports
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta

# Set up logging for development - Deactivate in prod mode
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
# load_dotenv(dotenv_path='/opt/hootguard/.env')

# --- API SCRIPTS ---
from scripts.pihole_get_data_from_api_summary import get_data_from_api_summary
# --- INITIAL_SETUP ---
from scripts.initial_setup_main import perform_initial_setup
# --- RESET ---
from scripts.reset_main import perform_reset
# --- FREE IP DETECTION ---
from scripts.network_free_ipv4 import find_free_ip
# --- DDNS ---
from scripts.ddns_configure_user_hootdns import ddns_activate_hootdns
from scripts.ddns_update_status_file import ddns_update_status
from scripts.ddns_change_crontab import ddns_update_crontab
from scripts.ddns_update_endpoint_in_global_config import replace_vpn_endpoint
from scripts.ddns_update_hootdns_global_config import ddns_update_hootdns_credentials
# --- OTHER SCRIPTS ---
from scripts.global_logger import logger
from scripts.global_config_loader import load_config
from scripts.system_reboot import reboot
# --- BLUEPRINTS ---
from blueprints.adblock.routes import adblock_bp # Import Adblock blueprint
from blueprints.ssh.routes import ssh_bp  # Import SSH blueprint
from blueprints.vpn.routes import vpn_bp  # Import VPN blueprint
from blueprints.ddns.routes import ddns_bp  # Import DDNS blueprint
from blueprints.snooze.routes import snooze_bp  # Import Snooze blueprint
from blueprints.network.routes import network_bp  # Import Network blueprint
from blueprints.status.routes import status_bp  # Import Status blueprint
from blueprints.password.routes import password_bp  # Import Password blueprint

# Load the global config
config = load_config()

# Access configuration values
PW_HASHED_PASSWORD_PATH = config['passwords']['hashed_password_path']
# Flag which, if the file does not exist, indicates the first start of HootGuard.
INITIALIZATION_FLAG = config['misc']['init_flag']
# Load environment variables from .env file
load_dotenv(dotenv_path=config['misc']['env_file_path'])

# Initialize Flask app
app = Flask(__name__)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Securely load environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SESSION_COOKIE_HTTPONLY'] = True # Prevent JavaScript access to session cookies 
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' # Protect against CSRF without being too restrictive
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Register the Blueprints
app.register_blueprint(adblock_bp) # Adblock blueprint
app.register_blueprint(ssh_bp)  # SSH blueprint
app.register_blueprint(vpn_bp)  # VPN blueprint
app.register_blueprint(ddns_bp)  # DDNS blueprint
app.register_blueprint(snooze_bp)  # Snooze blueprint
app.register_blueprint(network_bp)  # Network blueprint
app.register_blueprint(status_bp)  # Status blueprint
app.register_blueprint(password_bp)  # Password blueprint

# Function to read the hashed password from the file
def read_hashed_password():
    with open(PW_HASHED_PASSWORD_PATH, 'r') as file:
        return file.read().strip()

# Use the hash read from the file
password_hash = read_hashed_password()

# HOOTDNS - Check if hootdns subdomain and api key are in global config
def check_hootdns_config():
    try:
        sub = config['ddns']['user_hootdns_subdomain']
        key = config['ddns']['user_hootdns_api_key']
        if sub and key:
            print(f"DOMAIN: {sub}")
            print(f"KEY: {key}")
            return 'yes'
    except KeyError:
        pass
    return 'no'

# HOOTDNS - Configure and activate HootDNS
def activate_and_configure_hootdns(protocol: str):
    """
    Activates and configures HootDNS for the given protocol ('ipv4' or 'ipv6').
    Raises ValueError for unsupported values.
    """
    if protocol not in ['ipv4', 'ipv6']:
        raise ValueError(f"Unsupported protocol for HootDNS: {protocol}")

    user_key = f"user-hootdns-{protocol}"

    ddns_activate_hootdns(protocol)
    ddns_update_status(user_key)
    ddns_update_crontab(user_key)

    full_subdomain = get_hootdns_full_subdomain()
    if full_subdomain:
        replace_vpn_endpoint(full_subdomain)


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



# Logged in
def is_logged_in():
    return session.get('logged_in')


# --- Routes below ---

@app.before_request
def check_initialization_and_login_status():
    excluded_routes = [
        'login', 'logout', 'static', 
        'initial_setup_intro', 'initial_setup_network',
        'initial_setup_ddns', 'initial_setup_password',
        'initial_setup_summary', 'initial_setup_run',
        'initial_setup_handler', 'reboot_initial_setup'
]

    # Check if the system has been initialized
    if not os.path.exists(INITIALIZATION_FLAG) and request.endpoint not in excluded_routes:
        return redirect(url_for('initial_setup_intro'))

    # Check login status (only after initialization)
    if os.path.exists(INITIALIZATION_FLAG) and not is_logged_in() and request.endpoint not in excluded_routes:
        return redirect(url_for('login'))

# Initial Setup - Intro
@app.route('/initial_setup_intro', methods=['GET', 'POST'])
def initial_setup_intro():
    # Check is initial_setup was already completed
    if os.path.exists(INITIALIZATION_FLAG):
        return redirect(url_for('login'))
    # If initial_setup do below
    # Render the setup page
    return render_template('initial_setup/initial_setup_intro.html')

# Initial Setup - Network
@app.route('/initial_setup_network', methods=['GET', 'POST'])
def initial_setup_network():
    # Check is initial_setup was already completed
    if os.path.exists(INITIALIZATION_FLAG):
        return redirect(url_for('login'))

    # If initial_setup do below
    # Get suggested network settings
    suggested_ip, subnet_mask, standard_gw = find_free_ip()

    # Fallback values if no free IP is found
    suggested_ip = suggested_ip if suggested_ip else "Not available"
    subnet_mask = subnet_mask if subnet_mask else "Not available"
    standard_gw = standard_gw if standard_gw else "Not available"

    # Render the setup page
    return render_template('initial_setup/initial_setup_network.html', suggested_ip=suggested_ip, subnet_mask=subnet_mask, standard_gw=standard_gw)

# Initial Setup - Dynamic DNS
@app.route('/initial_setup_ddns', methods=['GET', 'POST'])
def initial_setup_ddns():
    # Check is initial_setup was already completed
    if os.path.exists(INITIALIZATION_FLAG):
        return redirect(url_for('login'))
    # If initial_setup do below
    hootdns = check_hootdns_config()
    return render_template('initial_setup/initial_setup_ddns.html', hootdns=hootdns)

# Initial Setup - Password
@app.route('/initial_setup_password', methods=['GET', 'POST'])
def initial_setup_password():
    # Check is initial_setup was already completed
    if os.path.exists(INITIALIZATION_FLAG):
        return redirect(url_for('login'))
    # If initial_setup do below
    # Render the setup page
    return render_template('initial_setup/initial_setup_password.html')

# Initial Setup - Summary
@app.route('/initial_setup_summary', methods=['GET', 'POST'])
def initial_setup_summary():
    # Check is initial_setup was already completed
    if os.path.exists(INITIALIZATION_FLAG):
        return redirect(url_for('login'))
    # If initial_setup do below
    # Render the setup page
    return render_template(
        'initial_setup/initial_setup_summary.html',
        ip_addr=session.get('ip_address', '—'),
        subnet=session.get('subnet_mask', '—'),
        gateway=session.get('standard_gateway', '—'),
        ipversion=session.get('ipversion', '—'),
        password=session.get('setup_password', '—'),
        hootdns_subdomain=session.get('hootdns_subdomain', ''),
        hootdns_api_key=session.get('hootdns_api_key', '')
    )

# Initial Setup Handler
@app.route('/initial_setup_handler', methods=['POST'])
def initial_setup_handler():
    step = request.form.get('step')

    if step == 'network':
        session['ip_address'] = request.form.get('ip_address')
        session['subnet_mask'] = request.form.get('subnet_mask')
        session['standard_gateway'] = request.form.get('standard_gateway')
        return redirect(url_for('initial_setup_ddns'))

    elif step == 'ddns':
        session['hootdns_subdomain'] = ''
        session['hootdns_api_key'] = ''
        session['ipversion'] = request.form.get('ipversion')
        # Only update HootDNS values if they were submitted in this form.
        # Prevents overwriting them if they're already set.
        if request.form.get('hootdns_subdomain'):
            session['hootdns_subdomain'] = request.form.get('hootdns_subdomain')
        if request.form.get('hootdns_api_key'):
            session['hootdns_api_key'] = request.form.get('hootdns_api_key')
        return redirect(url_for('initial_setup_password'))

    elif step == 'password':
        session['setup_password'] = request.form.get('new_password')
        return redirect(url_for('initial_setup_summary'))

    else:
        return redirect(url_for('initial_setup_intro'))


# Initital Setup Run
@app.route('/initial_setup_run', methods=['POST'])
def initial_setup_run():
    session.pop('logged_in', None)  # Log out the user

    # Optional: Write subdomain and API key to global_config.yaml
    subdomain = request.form.get('ddns_hootdns_subdomain')
    api_key = request.form.get('ddns_hootdns_api_key')
    if subdomain and api_key:
        if ddns_update_hootdns_credentials(subdomain, api_key):
            time.sleep(0.2) # slight delay to ensure file write completes
            config = load_config() # force reload config

    # HootDNS
    ddns_status = request.form.get('ddns_status', 'skip')  # Default to 'skip' if not provided
    if ddns_status == "ipv4":
        activate_and_configure_hootdns("ipv4")
    elif ddns_status == "ipv6":
        activate_and_configure_hootdns("ipv6")
    elif ddns_status == "skip":
        pass  # do nothing

    # Network & Password
    initial_setup_thread = threading.Thread(target=perform_initial_setup, args=(request.form['ip_address'], request.form['subnet_mask'], request.form['standard_gateway'], request.form['new_password'],))
    initial_setup_thread.start()
    return render_template('reboot/reboot_initial_setup.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    # Check if the user is temporarily locked out
    if 'failed_attempts' in session and session['failed_attempts'] >= 3:
        lockout_time = session.get('lockout_time', 0)
        time_since_lockout = time.time() - lockout_time

        # Enforce a 30-second lockout period
        if time_since_lockout < 30:
            remaining_time = int(30 - time_since_lockout)
            return render_template('login.html', wrong_password="tooManyTries")

        # Reset failed attempts after lockout period ends
        session['failed_attempts'] = 0

    # Check if password is correct
    if request.method == 'POST':
        password = request.form['password']
        if check_password_hash(password_hash, password):
            session.clear()
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            # Increment failed attempts in the session
            session['failed_attempts'] = session.get('failed_attempts', 0) + 1

            # If the user has 3 failed attempts, set the lockout time
            if session['failed_attempts'] >= 3:
                session['lockout_time'] = time.time()
                return render_template('login.html', wrong_password="lock_login")

            # Wrong password but not locked out
            return render_template('login.html', wrong_password="wrong_pwd")

    # Render login page without errors
    return render_template('login.html', wrong_password=None)

# Logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# Home
@app.route('/home', methods=['GET', 'POST'])
def home():
        # Specify the API parameters you want to fetch
        api_params = ['domains_being_blocked', 'dns_queries_today', 'ads_blocked_today', 'ads_percentage_today']

        # Fetch data from Pi-hole API
        data = get_data_from_api_summary(api_params)

        # Check if an update is available
        update_flag_path = "/opt/hootguard/misc/update_available"
        update_available = os.path.exists(update_flag_path)

        # Pass the fetched data and update status to the template
        return render_template('home.html', data=data, update_available=update_available)


# Settings
@app.route('/settings', methods=['GET', 'POST'])
def settings():
        return render_template('settings.html')

# System Update
@app.route('/system_update')
def system_update():
    status = request.args.get('status')
    if status == "start_update":
        subprocess.run(["sudo", "/usr/bin/python3", "/opt/hootguard/main/scripts/update/update_hootguard.py"], check=True)
    return render_template('system_update.html')

# System Reset
@app.route('/system_reset')
def system_reset():
    return render_template('system_reset.html')

# System Shutdown
@app.route('/system_shutdown', methods=['GET', 'POST'])
def system_shutdown():
    if request.method == 'POST':
        try:
            # Execute the shutdown command
            subprocess.run(['sudo', '/bin/systemctl', 'poweroff'], check=True)
            return jsonify({
                'message': 'System is shutting down.',
                'details': (
                    'This process typically takes 10–15 seconds. '
                    'To restart your system after the shutdown, unplug the power supply '
                    'and plug it back in to restart the HootGuard Sentry.'
                )
            }), 200
        except subprocess.CalledProcessError as e:
            return jsonify({'error': f'Shutdown failed: {str(e)}'}), 500

# Run System Reset
@app.route('/system_reset_perform')
def system_reset_perform():
        session.pop('logged_in', None)  # Log out the user
        factory_reset_thread = threading.Thread(target=perform_reset, args=("factory_reset",))
        factory_reset_thread.start()
        return render_template('reboot/reboot_reset.html')  # Render a page that will redirect the user

# Error
@app.route('/error')
def error():
        # Render an error page that allows the user to navigate back to the VPN settings page
        return render_template('error.html')

# 404 - Custom error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# 500 - Custom error handlers
@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Exception - Custom error handlers
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled Exception: {e}")
    return render_template('500.html'), 500

# Run the application
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1')
