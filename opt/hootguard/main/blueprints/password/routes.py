from flask import Blueprint, render_template, request, session, redirect
import threading
from scripts.password_save_and_reboot import password_save_and_reboot_system

# Create a blueprint for password management
password_bp = Blueprint('password', __name__)

# Password Settings - HootGuard
@password_bp.route('/password_settings', methods=['GET', 'POST'])
def password_settings():
        return render_template('password_settings.html')

# Password Change - HootGuard
@password_bp.route('/password_change', methods=['POST'])
def password_change():
    new_password = request.form['new_password']
    session.pop('logged_in', None)  # Log out the user
    password_change_thread = threading.Thread(target=password_save_and_reboot_system, args=(new_password,))
    password_change_thread.start()
    return render_template('reboot/reboot_password.html')  # Render a page that will redirect the user
