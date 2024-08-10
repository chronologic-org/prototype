from flask import Flask, jsonify, request, session, redirect
from flask_cors import CORS
from flask_session import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app, supports_credentials=True)

# Configure server-side session storage
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config.update(SESSION_COOKIE_SAMESITE=None, SESSION_COOKIE_SECURE=False)

Session(app)

# Path to the credentials JSON file
CREDENTIALS_FILE = os.getenv('CREDENTIALS_FILE')

# OAuth 2.0 scopes for the Google Calendar API
SCOPES = [os.getenv('SCOPES')]

# Redirect URI for OAuth 2.0
REDIRECT_URI = os.getenv('REDIRECT_URI')

STREAMLIT_URL = os.getenv('STREAMLIT_URL')

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Enable HTTP (insecure) for local testing

@app.route('/')
def index():
    return 'Welcome to Chronologic!'

@app.route('/authorize/<api_type>')
def authorize(api_type: str):
    if 'google_credentials' in session:
        return redirect(f'{STREAMLIT_URL}/?authorized=true')

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
    session.modified = True

    return redirect(authorization_url)

@app.route('/google/callback')
def callback():
    state = session.get('state')
    if not state:
        return 'State not found in session', 400

    if state != request.args.get('state'):
        return 'State mismatch error', 400

    flow = Flow.from_client_secrets_file(CREDENTIALS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['google_credentials'] = credentials_to_dict(credentials)
    
    # Debugging print statement
    print("Stored credentials in session:", session['google_credentials'])

    return redirect(f'{STREAMLIT_URL}/?authorized=true')

@app.route('/get_credentials')
def get_credentials():
    google_credentials = session.get('google_credentials')
    # Debugging print statement
    print("Retrieved credentials from session:", google_credentials)
    return jsonify(google_credentials)

@app.route('/calendar')
def calendar_events():
    google_credentials = session.get('google_credentials')
    if not google_credentials:
        print("Not authorized: No credentials found in session")
        return jsonify({'error': 'Not authorized'}), 401
    
    # Assuming CalendarService is correctly implemented
    calendar_service = CalendarService({'google': google_credentials})
    events = calendar_service.get_events()
    
    # Debugging print statement
    print("Events retrieved:", events)
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
