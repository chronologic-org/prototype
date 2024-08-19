# Chronologic Prototype

## Getting Started

### 0.1 Create Python environment and (only if first time)
```
pip install virtualenv
python -m venv .venv
```
### 0.2 Create environment file (.env)
Since this is a secret file, it cannot be put on Github and thus, someone needs to share it directly. It contains all API and secret keys, credentials, etc. 

### 0.3 Create secrets folder
This is where the Google API credentials are stored. Create the folder in the main directory. Then, download the credentials file from Google Console, APIs & Services/Credentials. The file name is prototype_web_client. Download, rename to `credentials.json` and place inside the secrets folder. 

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

## Future Improvements

- [ ] update_events

In its current form, the update_events function can change everyhting but the name of the event. This is because of the format of the llm response, which is the same as create_event. This means that we do not store the current name and return only the new name we want. 

This will cause an issue since to find the event we need to update, we need to know its name. Thus, it is required to give the update_event function both the current and the new name. For this, update the response format in the prompt. 

- [ ] Calendar instance

Currently, a new Calendar object is initialized every time any of the create, update or delete functions are called. This is alright for now, but with higher volume of requests will slow down the app. Find a way to initialize the calendar once per user. 

- [ ] Delete multiple events 

Find a way to request the deletion of multiple events on a date. This will likely require a new reponse format as you need to return a data to delete events on, not the name of an event to delete. 

- [ ] Error handling

Handle different errors in the llm response such as malformed json fields. 

*Example:* There is no recurrence requested, so the llm returns a json with recurrence where the recurrence fields are present, but they have no values. 
