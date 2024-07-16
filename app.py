from flask import Flask, jsonify, request, redirect, url_for, session
from flask_session import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
import os
from dotenv import load_dotenv
from calendar_clients import CalendarClientFactory
from services.calendar_service import CalendarService

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
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=False) #important for the authentication, not sure why

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
    print(f"Session in authorize: {session}")  # Debug statement
    print(session.get('google_credentials'))  # Debug statement
    if 'google_credentials' in session:
        # User is already authenticated
        # return redirect(url_for('calendar_events'))
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

    print(f"Session after storing credentials: {session}")  # Debug statement

    # return redirect(url_for('calendar_events'))
    return redirect(f'{STREAMLIT_URL}/?authorized=true')

@app.route('get_credentials')
def get_credentials():
    return jsonify(session)

@app.route('/calendar')
def calendar_events():
    # Collect credentials for both Google and Outlook from the session
    credentials_dict = {
        'google': session.get('google_credentials') if 'google_credentials' in session else None,
        'outlook': session.get('outlook_credentials') if 'outlook_credentials' in session else None
    }

    credentials_dict = {api_type: creds for api_type, creds in credentials_dict.items() if creds}
    
    calendar_service = CalendarService(credentials_dict)
    api_types = ['google']
    event = {
        'summary': 'Integration Test Event',
        'location': 'Integration Test Location',
        'description': 'An event created by an integration test',
        'start': {
            'dateTime': '2024-07-01T10:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': '2024-07-01T12:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        },
    }
    # result = calendar_service.create_event(api_types, event) #test event creation
    # result = calendar_service.update_event(api_types, 'Integration Test Event', event) #test event update
    # result = calendar_service.delete_event(api_types, 'Integration Test Event') #test event deletion
    # print(result)  # Print the result to see the event URL

    events = {}
    for api_type, client in calendar_service.clients.items():
        # Fetch events for the next 10 days from each calendar
        events[api_type] = client.get_events()

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
    with app.app_context():
        app.run(debug=True)
        
