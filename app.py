from flask import Flask, jsonify, request, session, redirect
# from flask_cors import CORS
# from flask_session import Session
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import jwt
import os
from dotenv import load_dotenv
from services.calendar_service import CalendarService

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
# CORS(app, supports_credentials=True)

# # Configure server-side session storage
# app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SESSION_FILE_DIR'] = './.flask_session/'
# app.config['SESSION_PERMANENT'] = False
# app.config['SESSION_USE_SIGNER'] = True
# app.config.update(SESSION_COOKIE_SAMESITE=None, SESSION_COOKIE_SECURE=False)

# Session(app)

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

@app.route('/authorize/google')
def authorize():
    flow = Flow.from_client_secrets_file(CREDENTIALS_FILE, scopes=SCOPES, redirect_uri=REDIRECT_URI)
    
    authorization_url, state = flow.authorization_url()
    session['state'] = state
    return redirect(authorization_url)

@app.route('/google/callback')
def callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(CREDENTIALS_FILE, scopes=SCOPES, state=state, redirect_uri=REDIRECT_URI)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    token = jwt.encode({'access_token': credentials.token}, 'SECRET_KEY', algorithm='HS256')
#     session['google_credentials'] = credentials_to_dict(credentials)
    
#     # Debugging print statement
#     print("Stored credentials in session:", session['google_credentials'])

    return redirect(f'{STREAMLIT_URL}/?token={token}')

def token_required(f):
    def wrap(*args, **kwargs):
        token = request.headers.get('Authorization').split()[1]
        try:
            jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return wrap

# @app.route('/get_credentials')
# def get_credentials():
#     google_credentials = session.get('google_credentials')
#     # Debugging print statement
#     print("Retrieved credentials from session:", google_credentials)
#     return jsonify(google_credentials)

@app.route('/calendar')
@token_required
def calendar_events():
    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])
    creds = Credentials(decoded['access_token'])
    
    # Assuming CalendarService is correctly implemented
    calendar_service = CalendarService({'google': creds})
    events = calendar_service.get_events()
    
    # Debugging print statement
    print("Events retrieved:", events)
    return jsonify(events)

# def credentials_to_dict(credentials):
#     return {
#         'token': credentials.token,
#         'refresh_token': credentials.refresh_token,
#         'token_uri': credentials.token_uri,
#         'client_id': credentials.client_id,
#         'client_secret': credentials.client_secret,
#         'scopes': credentials.scopes
#     }

if __name__ == '__main__':
    app.run(debug=True)
