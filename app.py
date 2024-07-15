from flask import Flask, jsonify, request, redirect, url_for, session
from flask_session import Session
from google.oauth2 import credentials as google_credentials
from google_auth_oauthlib.flow import Flow
import os
from dotenv import load_dotenv

from calendar_clients import CalendarClientFactory

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set the secret key from the .env file
app.secret_key = os.getenv('SECRET_KEY')

# Configure server-side session storage
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'flask_session:'  # Adding prefix to session keys
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True) #important for the authentication, not sure why
Session(app)

# Path to the credentials JSON file
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')

# OAuth 2.0 scopes for the Google Calendar API
SCOPES = [os.getenv('SCOPES')]

# Redirect URI for OAuth 2.0
REDIRECT_URI = os.getenv('REDIRECT_URI')

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Enable HTTP (insecure) for local testing

@app.route('/')
def index():
    return 'Welcome to Chronologic!'

@app.route('/authorize/<api_type>')
def authorize(api_type: str):
    if api_type == 'google':
        flow = Flow.from_client_secrets_file(CREDENTIALS_FILE, scopes=SCOPES)
    else:
        return 'Unsupported API type', 400

    flow.redirect_uri = REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state
    session['api_type'] = api_type

    # Debugging statements
    print(f"State set in session: {state}")
    print(f"Authorization URL: {authorization_url}")
    print(f"Session before redirect: {session}")

    return redirect(authorization_url)

@app.route('/<api_type>/callback')
def callback(api_type: str):
    print(f"Session in callback: {session}")  # Debug statement
    state = session.get('state')
    if not state:
        print(f"Session state is missing. Session: {session}")
        return 'State not found in session', 400

    request_state = request.args.get('state')
    print(f"State in session: {state}")  # Debug statement
    print(f"State in request: {request_state}")  # Debug statement

    if state != request_state:
        return 'State mismatch error', 400

    if api_type == 'google':
        flow = Flow.from_client_secrets_file(
            CREDENTIALS_FILE, scopes=SCOPES, state=state)
    else:
        return 'Unsupported API type', 400

    flow.redirect_uri = REDIRECT_URI

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session
    credentials = flow.credentials
    session[f'{api_type}_credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('calendar_events'))

@app.route('/calendar')
def calendar_events():
    # Collect credentials for both Google and Outlook from the session
    credentials_dict = {
        'google': session.get('google_credentials') if 'google_credentials' in session else None,
        'outlook': session.get('outlook_credentials') if 'outlook_credentials' in session else None
    }

    credentials_dict = {api_type: creds for api_type, creds in credentials_dict.items() if creds}

    # Initialize clients for both Google and Outlook
    clients = CalendarClientFactory.get_clients(credentials_dict)

    events = {}
    for api_type, client in clients.items():
        # Fetch events for the next 10 days from each calendar
        events[api_type] = client.get_events('primary', '10')

    return jsonify(events)

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

if __name__ == '__main__':
    app.run(debug=True)
