# Chronologic Prototype

## Getting Started

### 0.1 Create Python environment and (only if first time)
```
pip install virtualenv
python -m venv .venv
```
### 0.2 Create environment file (.env)
Since this is a secret file, it cannot be put on Github and thus, someone needs to share it directly. It contains all API and secret keys, credentials, etc. 

### 1. Activate Python environment

Windows: 

`.venv\Scripts\activate`

macOS and Linux:

`source .venv/bin/activate`

### 2. Update dependencies
`pip install -r requirements.txt`

### 3. Start Flask server
`flask run`

### 4. Start Streamlit interface
`streamlit run streamlit_UI.py`

## Important

### Flask APIs:

When a change is made to an API, a restart of that Flask server is needed for the change to take effect. Simply stop the current process, then start the Flask server again. 

### Google Credentials and Auth

Everything Google can be found on the Google console, account is the Chronologic account. 

#### Credentials

The OAuth 2.0 credentials can be found under APIs & Services/Credentials. Here, you can obtain the credentials used to authorize the Google APIs usage and create new ones. 

#### Allowed users

Since this is a test app, Google requires that users added as test users in order to be able to log in. Current test users can be seen and new users can be added in APIs & Services/OAuth consent screen.

### Groq API

You can find the Groq API key in the Groq platform. 
