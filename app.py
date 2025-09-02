import base64
import json
import os
import time
from datetime import datetime
from functools import wraps
from flask import (Flask, jsonify, request, Response, render_template,
                   redirect, url_for, flash, session)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- CONFIGURATION ---
ADMIN_PASSWORD = "Aa@14041404"
SUBS_FILE = 'subscriptions.json'
USERS_FILE = 'users.json'
CUSTOM_SUBS_FILE = 'custom_subs.json'
CACHE_DURATION = 600  # 10 minutes
SUBS_CACHE = {}

# --- DATA MANAGEMENT ---

def load_data(filepath, default_data={}):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        save_data(filepath, default_data)
        return default_data

def save_data(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- INITIAL DATA LOAD ---
USER_DATA = load_data(USERS_FILE, {})
SUBSCRIPTION_LINKS = load_data(SUBS_FILE, {"normal": [], "fullnormal": [], "fragment": []})
CUSTOM_SUBS = load_data(CUSTOM_SUBS_FILE, {})

# --- DECORATORS & HELPERS ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def fetch_and_parse_links(links):
    import requests
    all_servers = []
    current_time = time.time()
    for link in links:
        if link in SUBS_CACHE and current_time - SUBS_CACHE[link]['timestamp'] < CACHE_DURATION:
            all_servers.extend(SUBS_CACHE[link]['data'])
            continue
        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            decoded_content = base64.b64decode(response.text).decode('utf-8')
            servers = [line.strip() for line in decoded_content.splitlines() if line.strip()]
            SUBS_CACHE[link] = {'data': servers, 'timestamp': current_time}
            all_servers.extend(servers)
        except Exception as e:
            print(f"Error with link {link}: {e}")
    return "\n".join(all_servers)

def log_user_usage(username, sub_type_or_name):
    if username not in USER_DATA:
        USER_DATA[username] = {"limit": -1, "usage": {}, "last_seen": None}
    
    user = USER_DATA[username]
    current_usage = user['usage'].get(sub_type_or_name, 0)
    user['usage'][sub_type_or_name] = current_usage + 1
    user['last_seen'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_data(USERS_FILE, USER_DATA)
    return user

# --- ADMIN ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Incorrect password.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin_panel():
    return render_template('admin.html', users=USER_DATA, subscriptions=SUBSCRIPTION_LINKS)

@app.route('/admin/add_user', methods=['POST'])
@login_required
def add_user():
    username = request.form.get('username', '').strip()
    if username and username not in USER_DATA:
        USER_DATA[username] = {"limit": -1, "usage": {}, "last_seen": None}
        save_data(USERS_FILE, USER_DATA)
        flash(f'User "{username}" created successfully.', 'success')
    else:
        flash('Username is invalid or already exists.', 'error')
    return redirect(url_for('admin_panel'))

@app.route('/admin/set_limit', methods=['POST'])
@login_required
def set_limit():
    username = request.form.get('username')
    try:
        limit = int(request.form.get('limit'))
        if username in USER_DATA:
            USER_DATA[username]['limit'] = limit
            save_data(USERS_FILE, USER_DATA)
            flash(f"Limit for {username} updated to {limit}.", 'success')
    except (ValueError, TypeError):
        flash("Invalid limit value.", 'error')
    return redirect(url_for('admin_panel'))

# ******** ADDED MISSING FUNCTIONS ********
@app.route('/admin/add_sub', methods=['POST'])
@login_required
def add_sub():
    """Adds a new public subscription link."""
    sub_type = request.form.get('sub_type')
    sub_url = request.form.get('sub_url', '').strip()

    if sub_type in SUBSCRIPTION_LINKS and sub_url:
        if sub_url not in SUBSCRIPTION_LINKS[sub_type]:
            SUBSCRIPTION_LINKS[sub_type].append(sub_url)
            save_data(SUBS_FILE, SUBSCRIPTION_LINKS)
            flash("Subscription link added successfully.", 'success')
        else:
            flash("This link already exists.", 'warning')
    else:
        flash("Invalid data provided.", 'error')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/delete_sub', methods=['POST'])
@login_required
def delete_sub():
    """Deletes a public subscription link."""
    sub_type = request.form.get('sub_type')
    sub_url = request.form.get('sub_url')

    if sub_type in SUBSCRIPTION_LINKS and sub_url in SUBSCRIPTION_LINKS[sub_type]:
        SUBSCRIPTION_LINKS[sub_type].remove(sub_url)
        save_data(SUBS_FILE, SUBSCRIPTION_LINKS)
        flash("Subscription link deleted successfully.", 'success')
    else:
        flash("Link not found.", 'error')
        
    return redirect(url_for('admin_panel'))
# ******** END OF ADDED FUNCTIONS ********


# --- PUBLIC & USER-SPECIFIC SUBSCRIPTION ROUTES ---

@app.route('/sub/usage')
def get_usage():
    return jsonify(USER_DATA)

@app.route('/sub/<sub_type>')
def get_public_subscription(sub_type):
    if sub_type not in SUBSCRIPTION_LINKS:
        return jsonify({"error": "Subscription type not found"}), 404
    
    username = request.args.get('name', '__anonymous__')
    user_data = log_user_usage(username, sub_type)

    if user_data['limit'] != -1 and user_data['usage'].get(sub_type, 0) > user_data['limit']:
        return jsonify({"error": "Usage limit reached"}), 429

    links = SUBSCRIPTION_LINKS.get(sub_type, [])
    content = fetch_and_parse_links(links)
    return Response(base64.b64encode(content.encode()).decode(), mimetype='text/plain')


@app.route('/sub/custom/<name>')
def get_custom_subscription(name):
    if name not in CUSTOM_SUBS:
        return jsonify({"error": "Custom subscription not found"}), 404

    log_user_usage(name, 'custom')
    
    configs = CUSTOM_SUBS[name].get('configs', [])
    content = "\n".join(configs)
    return Response(base64.b64encode(content.encode()).decode(), mimetype='text/plain')


# --- USER PANEL FOR CREATING SUBS ---

@app.route('/sub/make', methods=['GET', 'POST'])
def make_sub_home():
    if request.method == 'POST':
        sub_name = request.form.get('sub_name', '').strip()
        if sub_name:
            if sub_name not in CUSTOM_SUBS:
                CUSTOM_SUBS[sub_name] = {'configs': []}
                save_data(CUSTOM_SUBS_FILE, CUSTOM_SUBS)
                if sub_name not in USER_DATA:
                    USER_DATA[sub_name] = {"limit": -1, "usage": {}, "last_seen": None}
                    save_data(USERS_FILE, USER_DATA)
            return redirect(url_for('manage_sub', name=sub_name))
        else:
            flash('Subscription name cannot be empty.', 'error')
    return render_template('make_sub.html')


@app.route('/sub/make/<name>', methods=['GET', 'POST'])
def manage_sub(name):
    if name not in CUSTOM_SUBS:
        return redirect(url_for('make_sub_home'))

    if request.method == 'POST':
        new_configs = request.form.get('configs', '').strip().splitlines()
        if new_configs:
            CUSTOM_SUBS[name]['configs'].extend(c.strip() for c in new_configs if c.strip())
            save_data(CUSTOM_SUBS_FILE, CUSTOM_SUBS)
            flash(f'{len(new_configs)} new configurations added.', 'success')
            return redirect(url_for('manage_sub', name=name))

    sub_data = CUSTOM_SUBS.get(name)
    user_usage_data = USER_DATA.get(name)
    full_sub_url = url_for('get_custom_subscription', name=name, _external=True)

    return render_template('user_panel.html', 
                           name=name, 
                           sub_data=sub_data,
                           user_data=user_usage_data,
                           full_sub_url=full_sub_url)

@app.route('/sub/make/<name>/delete', methods=['POST'])
def delete_config(name):
    config_to_delete = request.form.get('config')
    if name in CUSTOM_SUBS and config_to_delete in CUSTOM_SUBS[name]['configs']:
        CUSTOM_SUBS[name]['configs'].remove(config_to_delete)
        save_data(CUSTOM_SUBS_FILE, CUSTOM_SUBS)
        flash('Configuration deleted.', 'success')
    else:
        flash('Configuration not found.', 'error')
    return redirect(url_for('manage_sub', name=name))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

