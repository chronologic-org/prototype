from functools import wraps
import json
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
from services import llm_service

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

llm = llm_service.init_llm()

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
    credentials = credentials_to_dict(credentials)
    token = jwt.encode(credentials, app.secret_key, algorithm='HS256')
    return redirect(f'{STREAMLIT_URL}/?token={token}')

def token_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        token = request.headers.get('Authorization').split()[1]
        try:
            jwt.decode(token, app.secret_key, algorithms=['HS256'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403
        return f(*args, **kwargs)
    return wrap

@app.route('/calendar')
@token_required
def calendar_events():
    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, app.secret_key, algorithms=['HS256'])
    calendar_service = CalendarService({'google': decoded})
    google_service = calendar_service.clients['google'].service
    calendar = google_service.calendarList().get(calendarId='primary').execute()
    calendar_id = calendar['id']
    timezone = calendar['timeZone']
    calendar_name = calendar['summary']
    embed_link = f"https://calendar.google.com/calendar/embed?src={calendar_id}&ctz={timezone}"
    
    return jsonify({
        'calendar_name': calendar_name,
        'embed_link': embed_link
    })

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    
    response = llm_service.chat(prompt, llm)
    return jsonify(response)

@app.route('/create_event', methods=['POST'])
@token_required
def create_event():
    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, app.secret_key, algorithms=['HS256'])
    data = request.get_json()
    event = data.get('event')
    api_types = ['google']

    if not event:
        return jsonify({"error": "Event is required"}), 400
    if not api_types:
        return jsonify({"error": "API types are required"}), 400
    
    calendar_service = CalendarService({'google': decoded})
    response = calendar_service.create_event(api_types, event)
    
    return jsonify({"message": response})

@app.route('/update_event', methods=['POST'])
@token_required
def update_event():
    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, app.secret_key, algorithms=['HS256'])
    data = request.get_json()
    event = data.get('event')
    updated_event = event
    event_name = event.get('summary')
    api_types = ['google']

    if not event_name:
        return jsonify({"error": "Event name is required"}), 400
    if not updated_event:
        return jsonify({"error": "Updated event is required"}), 400
    if not api_types:
        return jsonify({"error": "API types are required"}), 400
    
    calendar_service = CalendarService({'google': decoded})
    response = calendar_service.update_event(api_types, event_name, updated_event)
    return jsonify({"message": response})

@app.route('/delete_event', methods=['POST'])
@token_required
def delete_event():
    token = request.headers.get('Authorization').split()[1]
    decoded = jwt.decode(token, app.secret_key, algorithms=['HS256'])
    data = request.get_json()
    event = data.get('event')
    event_name = event.get('summary')
    api_types = ['google']

    if not event_name:
        return jsonify({"error": "Event name is required"}), 400
    if not api_types:
        return jsonify({"error": "API types are required"}), 400
    
    calendar_service = CalendarService({'google': decoded})
    response = calendar_service.delete_event(api_types, event_name)
    return jsonify({"message": response})
    

if __name__ == '__main__':
    app.run(debug=True)
