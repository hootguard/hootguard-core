from flask import Blueprint, request, render_template, redirect
from scripts.snooze_read_status import snooze_read_status_and_return_status
from scripts.snooze_update_status_file import snooze_update_time

# Create the Snooze Blueprint
snooze_bp = Blueprint('snooze', __name__)

@snooze_bp.route('/snooze_settings', methods=['GET', 'POST'])
def snooze_settings():
        status_snooze = snooze_read_status_and_return_status()
        nts = request.args.get('nts')
        return render_template('snooze_settings.html', snooze_status=status_snooze, new_time_set=nts)

@snooze_bp.route('/snooze_change', methods=['GET', 'POST'])
def snooze_change():
        snooze_update_time(request.form['snooze_time'])
        return redirect('/snooze_settings?nts=True')
