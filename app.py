from flask import Flask, jsonify, request, redirect, url_for, session
from google.oauth2 import credentials as google_credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

from calendar_clients import CalendarClientFactory

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Set the secret key from the .env file
app.secret_key = os.getenv('SECRET_KEY')

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
    return redirect(authorization_url)

@app.route('/<api_type>/callback')
def callback(api_type: str):
    state = session.get('state')
    if not state:
        return 'State not found in session', 400

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

    return redirect(url_for('calendar_events', api_type=api_type))

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