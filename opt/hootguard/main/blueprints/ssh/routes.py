from flask import Blueprint, request, render_template, redirect, url_for, session
import os
import subprocess
from scripts.ssh_control_service import check_ssh_status, enable_ssh, disable_ssh
#from scripts.global_config import SSH_FIRST_TIME_FLAG_PATH
from scripts.global_config_loader import load_config

# Load the global config
config = load_config()

# Access configuration values
SSH_FIRST_TIME_FLAG_PATH = config['ssh']['first_time_flag_path']

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

    # Handle GET requests and retrieve the 'new_rem_acc_set' from the URL
    new_rem_acc_set = request.args.get('new_rem_acc_set')

    # Convert 'new_rem_acc_set' from string to boolean if it exists
    if new_rem_acc_set is not None:
        new_rem_acc_set = new_rem_acc_set.lower() == 'true'

    # Render the template with SSH status and success/error indicator
    return render_template('ssh/ssh_settings.html', ssh_status_message=ssh_status, new_rem_acc_set=new_rem_acc_set)


# SSH Set Password Route
@ssh_bp.route('/ssh_set_password', methods=['GET', 'POST'])
def ssh_set_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Update the SSH password (for the default user 'hootguard')
        try:
            user = 'hootguard'
            subprocess.run(['sudo', 'passwd', user], input=f'{new_password}\n{new_password}\n', text=True)

            # Create the flag file to mark SSH as activated
            with open(SSH_FIRST_TIME_FLAG_PATH, 'w') as f:
                f.write('SSH activated')

            # Now enable SSH after setting the password
            if enable_ssh():
                # flash('SSH has been activated and password has been set', 'success')
                new_rem_acc_set = True
            else:
                # flash('Failed to activate SSH', 'danger')
                new_rem_acc_set = False

            #return redirect(url_for('ssh_settings'))
            return redirect(url_for('ssh.ssh_settings', new_rem_acc_set=new_rem_acc_set))

        except Exception as e:
            flash(f'Failed to set SSH password: {e}', 'danger')
            return redirect(url_for('ssh.ssh_set_password'))

    return render_template('ssh/ssh_set_password.html')
