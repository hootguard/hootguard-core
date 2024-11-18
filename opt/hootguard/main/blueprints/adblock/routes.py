from flask import Blueprint, request, render_template, redirect, url_for
from scripts.adblock_update_status_file import adblock_read_status_file, adblock_profile_change
from scripts.adblock_add_entry_to_customlists import add_to_blacklist, add_to_whitelist
from scripts.adblock_read_entries_from_customlists import get_entires_from_customlists
from scripts.adblock_remove_entry_from_customlists import delete_from_blacklist, delete_from_whitelist

# Create the Blueprint
adblock_bp = Blueprint('adblock', __name__)

# Define your routes within the Blueprint
@adblock_bp.route('/adblock_profiles', methods=['GET', 'POST'])
def adblock_profiles():
        status = adblock_read_status_file()
        adblockProUpdSuc = request.args.get('adblockProUpdSuc')
        return render_template('adblock/adblock_profiles.html', status=status, adblock_profile_update_successful = adblockProUpdSuc)


@adblock_bp.route('/adblock_profiles_change', methods=['GET', 'POST'])
def adblock_profiles_change():
        adblock_profile_change(request.form)
        return redirect('/adblock_profiles?adblockProUpdSuc=True')
@adblock_bp.route('/adblock_manage_blacklist', methods=['GET', 'POST'])


def adblock_manage_blacklist():
    blacklistEntries = get_entires_from_customlists('black')
    listUpdateStatus = request.args.get('ListUpdSta', 'noStatus')
    return render_template('adblock/adblock_manage_blacklist.html', list_update_status=listUpdateStatus, blacklist_entries=blacklistEntries)


@adblock_bp.route('/adblock_add_to_blacklist', methods=['GET', 'POST'])
def adblock_add_to_blacklist():
    url = request.form.get('blacklisting')
    status = add_to_blacklist(url)
    return redirect(url_for('adblock.adblock_manage_blacklist', ListUpdSta=status))


@adblock_bp.route('/adblock_delete_from_blacklist', methods=['GET', 'POST'])
def adblock_delete_from_blacklist():
    entriesToDelete = request.form.getlist('entries_to_delete')
    delete_from_blacklist(entriesToDelete)
    return redirect(url_for('adblock.adblock_manage_blacklist', ListUpdSta='deleted'))


@adblock_bp.route('/adblock_manage_whitelist', methods=['GET', 'POST'])
def adblock_manage_whitelist():
    whitelistEntries = get_entires_from_customlists('white')
    listUpdateStatus = request.args.get('ListUpdSta', 'noStatus')
    return render_template('adblock/adblock_manage_whitelist.html', list_update_status=listUpdateStatus, whitelist_entries=whitelistEntries)


@adblock_bp.route('/adblock_add_to_whitelist', methods=['GET', 'POST'])
def adblock_add_to_whitelist():
    url = request.form.get('whitelisting')
    status = add_to_whitelist(url)
    return redirect(url_for('adblock.adblock_manage_whitelist', ListUpdSta=status))


@adblock_bp.route('/adblock_delete_from_whitelist', methods=['GET', 'POST'])
def adblock_delete_from_whitelist():
    entriesToDelete = request.form.getlist('entries_to_delete')
    delete_from_whitelist(entriesToDelete)
    return redirect(url_for('adblock.adblock_manage_whitelist', ListUpdSta='deleted'))
