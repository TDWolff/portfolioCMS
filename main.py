import flask
from flask import session, request, redirect, url_for
from functools import wraps
import secrets
import os
from apis.registry import registryUSRLOGIN
from apis.website_manager import get_all_websites, add_website, update_website_status, delete_website, edit_website, repair_csv_file
from apis.serversService import start, stop

app = flask.Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return flask.render_template('index.html')

@app.route('/servers')
@login_required
def servers():
    return flask.render_template('servers.html')


@app.route('/login', methods=['GET'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return flask.render_template('login.html')

@app.route('/start', methods=['POST'])
def startService():
    data = flask.request.get_json()
    id = data.get('id')
    print(f"Starting server with id: {id}...")
    return start(id)
    
@app.route('/stop', methods=['POST'])
def stopService():
    data = flask.request.get_json()
    id = data.get('id')
    print(f"Stopping server with id: {id}...")
    return stop(id)

@app.route('/loginUSR', methods=['POST'])
def loginUSR():
    data = flask.request.get_json()
    usr = data.get('username')
    pswd = data.get('password')
    print(f"Username: {usr}, Password: {pswd}")
    result = registryUSRLOGIN(usr, pswd)
    
    if "successfully" in result:
        session['user_id'] = usr
        session['logged_in'] = True
        return flask.jsonify({"success": True, "message": result}), 200
    else:
        return flask.jsonify({"success": False, "error": result}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return flask.jsonify({"success": True, "message": "Logged out"}), 200

@app.route('/api/websites', methods=['GET'])
@login_required
def get_websites():
    """Get all websites"""
    try:
        websites = get_all_websites()
        return flask.jsonify({"success": True, "websites": websites}), 200
    except Exception as e:
        print(f"Error in get_websites: {e}")
        return flask.jsonify({"success": False, "error": "Failed to load websites"}), 500
    
@app.route('/api/repair-csv', methods=['POST'])
@login_required
def repair_csv():
    """Repair malformed CSV file"""
    try:
        repair_csv_file()
        return flask.jsonify({"success": True, "message": "CSV file repaired"}), 200
    except Exception as e:
        return flask.jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/websites', methods=['POST'])
@login_required
def add_new_website():
    """Add a new website"""
    data = flask.request.get_json()
    name = data.get('name')
    url = data.get('url')
    
    if not name or not url:
        return flask.jsonify({"success": False, "error": "Name and URL are required"}), 400
    
    try:
        website = add_website(name, url)
        return flask.jsonify({"success": True, "website": website}), 200
    except Exception as e:
        return flask.jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/websites/test', methods=['POST'])
@login_required
def test_website_status():
    """Test and update website status"""
    data = flask.request.get_json()
    name = data.get('name')
    url = data.get('url')
    
    print(f"Testing website: {name} at URL: {url}")
    
    if not name or not url:
        return flask.jsonify({"success": False, "error": "Name and URL are required"}), 400
    
    try:
        from apis.websiteQuery import testWebsite
        direct_test_result = testWebsite(url)
        print(f"Direct test result for {url}: {direct_test_result}")
        
        websites = update_website_status(name, url)
        from apis.website_manager import normalize_url
        normalized_url = normalize_url(url)
        updated_website = next((w for w in websites if w['name'] == name and normalize_url(w['url']) == normalized_url), None)
        
        if updated_website:
            print(f"Updated website status: {updated_website}")
            return flask.jsonify({"success": True, "website": updated_website}), 200
        else:
            print(f"Website not found after update: {name}, {normalized_url}")
            return flask.jsonify({"success": False, "error": "Website not found"}), 404
            
    except Exception as e:
        print(f"Error in test_website_status: {e}")
        return flask.jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/websites', methods=['DELETE'])
@login_required
def delete_existing_website():
    """Delete a website"""
    data = flask.request.get_json()
    name = data.get('name')
    url = data.get('url')
    
    if not name or not url:
        return flask.jsonify({"success": False, "error": "Name and URL are required"}), 400
    
    try:
        delete_website(name, url)
        return flask.jsonify({"success": True, "message": "Website deleted"}), 200
    except Exception as e:
        return flask.jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/websites', methods=['PUT'])
@login_required
def edit_existing_website():
    """Edit a website"""
    data = flask.request.get_json()
    old_name = data.get('old_name')
    old_url = data.get('old_url')
    new_name = data.get('new_name')
    new_url = data.get('new_url')
    
    if not all([old_name, old_url, new_name, new_url]):
        return flask.jsonify({"success": False, "error": "All fields are required"}), 400
    
    try:
        websites = edit_website(old_name, old_url, new_name, new_url)
        updated_website = next((w for w in websites if w['name'] == new_name and w['url'] == new_url), None)
        return flask.jsonify({"success": True, "website": updated_website}), 200
    except Exception as e:
        return flask.jsonify({"success": False, "error": str(e)}), 500

@app.route('/pokeURL', methods=['POST'])
@login_required
def pokeURL():
    data = flask.request.get_json()
    url = data.get('url')
    from apis.websiteQuery import testWebsite
    result = testWebsite(url)
    if result:
        print(f"Website {url} is reachable.")
        return flask.jsonify({"success": True, "message": f"Website {url} is reachable."}), 200
    else:
        print(f"Website {url} is not reachable.")
        return flask.jsonify({"success": False, "error": f"Website {url} is not reachable."}), 400

@app.after_request
def after_request(response):
    # Updated CSP to allow external connections for website testing
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self'; "
        "img-src 'self' data:; "
        "connect-src 'self' https: http:;"  # Allow connections to any HTTPS/HTTP site for testing
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == "__main__":
    boolean_debug = True
    if not boolean_debug:
        app.run(debug=False, host="127.0.0.1", port="8454", ssl_context='adhoc')
    if boolean_debug:
        app.run(debug=True, host="0.0.0.0", port="8454")