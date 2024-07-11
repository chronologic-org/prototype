from flask import Flask, request, redirect, url_for, session
from google.oauth2 import credentials as google_credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

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

@app.route('/authorize')
def authorize():
    # Create OAuth2 flow instance
    flow = Flow.from_client_secrets_file(CREDENTIALS_FILE, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    # Store the state in the session to verify the callback request
    session['state'] = state
    print(f"State saved in session: {state}")

    return redirect(authorization_url)

@app.route('/google/callback')
def callback():
    print("Session contents:", session)
    state = session.get('state')
    if not state:
        return 'State not found in session', 400

    flow = Flow.from_client_secrets_file(
        CREDENTIALS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = REDIRECT_URI

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('calendar_events'))

@app.route('/calendar')
def calendar_events():
    # Load the credentials from the session
    credentials = google_credentials.Credentials(**session['credentials'])

    service = build('calendar', 'v3', credentials=credentials)

    # Get the user's primary calendar events
    events_result = service.events().list(calendarId='primary', maxResults=10).execute()
    events = events_result.get('items', [])

    # Display the events
    events_list = '<h1>Upcoming Events</h1>'
    if not events:
        events_list += '<p>No upcoming events found.</p>'
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        events_list += f'<p>{start} - {event["summary"]}</p>'

    return events_list

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