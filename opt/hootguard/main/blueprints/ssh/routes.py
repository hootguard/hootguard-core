from flask import Blueprint, request, render_template, redirect, url_for, session
from werkzeug.security import check_password_hash
import os
import subprocess # nosec

from scripts.ssh_control_service import check_ssh_status, enable_ssh, disable_ssh
#from scripts.global_config import SSH_FIRST_TIME_FLAG_PATH
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
SSH_FIRST_TIME_FLAG_PATH = config['ssh']['first_time_flag_path']
PW_HASHED_PASSWORD_PATH = config['passwords']['hashed_password_path']

# Function to read the hashed password from the file
def read_hashed_password():
    with open(PW_HASHED_PASSWORD_PATH, 'r') as file:
        return file.read().strip()

# Use the hash read from the file
password_hash = read_hashed_password()

# Create the SSH Blueprint
ssh_bp = Blueprint('ssh', __name__)

# SSH Settings Route
@ssh_bp.route('/ssh_settings', methods=['GET', 'POST'])
def ssh_settings():
    # Check current SSH status (true if SSH is active, false if it's deactivated)
    ssh_status = check_ssh_status()

    # Check if it's the first time SSH is being activated
    # first_time = True if SSH_FIRST_TIME_FLAG_PATH file does not exist
    # The flag file will be created after the ssh was activated the first time
    first_time = not os.path.exists(SSH_FIRST_TIME_FLAG_PATH)

    new_rem_acc_set = None  # Store whether SSH was successfully updated or not

    # Handle POST requests for enabling or disabling SSH
    if request.method == 'POST':
        if 'enable' in request.form:
            if first_time:
                # Redirect to password setup if SSH is being activated for the first time
                return redirect(url_for('ssh.ssh_set_password'))
            else:
                if enable_ssh():
                    new_rem_acc_set = True
                else:
                    new_rem_acc_set = False
        elif 'disable' in request.form:
            if disable_ssh():
                new_rem_acc_set = True
            else:
                new_rem_acc_set = False

        return redirect(url_for('ssh.ssh_settings', new_rem_acc_set=new_rem_acc_set))

    # Handle GET requests and retrieve the 'new_rem_acc_set' and 'new_ssh_password' from the URL
    new_rem_acc_set = request.args.get('new_rem_acc_set')
    new_ssh_password = request.args.get('new_ssh_password')

    # Convert 'new_rem_acc_set' from string to boolean if it exists
    if new_rem_acc_set is not None:
        new_rem_acc_set = new_rem_acc_set.lower() == 'true'

    # Render the template with SSH status and success/error indicator
    return render_template('ssh/ssh_settings.html', ssh_status_message=ssh_status, new_rem_acc_set=new_rem_acc_set, new_ssh_password=new_ssh_password)


# SSH Set Password Route
@ssh_bp.route('/ssh_set_password', methods=['GET', 'POST'])
def ssh_set_password():
    if request.method == 'POST':
        login_password = request.form['login_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Validate HootGuard login password
        if not check_password_hash(password_hash, login_password):
            print("Incorrect HootGuard login Password")
            return redirect('ssh_set_password?login_pwd=False')

        # Initialize `new_rem_acc_set` and `new_ssh_password`
        new_rem_acc_set = False

        # Update the SSH password (for the default user 'hootguard')
        try:
            user = 'hootguard'
            result = subprocess.run(
                ['/usr/bin/sudo', '/usr/local/bin/hootguard', 'set-password', user, new_password],
                capture_output=True, text=True, check=True
            )

            # Create the flag file to mark SSH as activated
            with open(SSH_FIRST_TIME_FLAG_PATH, 'w') as f:
                f.write('SSH activated')

            # Now enable SSH after setting the password
            if enable_ssh():
                print('SSH has been activated and password has been set', 'success')
                new_rem_acc_set = True
            else:
                print('Failed to activate SSH', 'danger')

        except subprocess.CalledProcessError as e:
            print(f'Failed to set password: {e}')
        except Exception as e:
            print(f'Failed to set SSH password: {e}', 'danger')

        # Redirect to settings with new_rem_acc_set
        return redirect(url_for('ssh.ssh_settings', new_rem_acc_set=new_rem_acc_set))

    #If the password is wrong, call the same login page again with the message wrong password
    login_pwd = request.args.get('login_pwd')
    return render_template('ssh/ssh_set_password.html', login_password=login_pwd)
    #return render_template('ssh/ssh_set_password.html')
