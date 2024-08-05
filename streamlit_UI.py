from flask import session
import streamlit as st
import random, requests
from services import llm_service
from streamlit_cookies_manager import EncryptedCookieManager
from services.calendar_service import CalendarService

# calendar = None

#Initiate the cookie manager
cookies = EncryptedCookieManager(prefix="cal1", password="password")
session = requests.Session()

if not cookies.ready():
    st.stop()

def initiate_authorization():
    auth_url = 'http://localhost:5000/authorize/google'
    return auth_url

    

# Function to pick 3 unique suggestions
def pick_suggestions(recommended_suggestions):
    if len(recommended_suggestions) < 3:
        raise ValueError("The list must contain at least 3 suggestions.")
    
    # Randomly choose 3 unique suggestions
    return random.sample(recommended_suggestions, 3)

# Exhaustive list of suggestions
recommended_suggestions = [
    "Create a new event for the team meeting at 10 AM tomorrow",
    "Delete the lunch meeting scheduled for Friday",
    "Update the project review meeting to 3 PM instead of 2 PM",
    "Set up a recurring event for daily stand-up meetings at 9 AM",
    "Cancel the one-on-one meeting with John next Monday",
    "Move the weekly sync meeting to Wednesdays at 4 PM",
    "Add a reminder for the dentist appointment next Thursday",
    "Schedule a call with the client on Tuesday at 11 AM",
    "Reschedule the board meeting to next Friday at 2 PM",
    "Remove the dinner reservation from the calendar",
    "Change the location of the quarterly review meeting to the main office",
    "Set a meeting with the marketing team at 1 PM on Thursday",
    "Clear all events from the calendar on Sunday",
    "Adjust the start time of the training session to 9:30 AM",
    "Add a new event for the software release on August 1st",
    "Delete the outdated conference call on the calendar",
    "Update the status meeting to be an all-day event",
    "Set a personal appointment for a haircut on Saturday at 10 AM",
    "Cancel the weekend workshop scheduled for next month",
    "Move the brainstorming session to the afternoon at 2 PM"
]

# Ensure Streamlit's session state is initialized for picked_suggestions
if "picked_suggestions" not in st.session_state:
    st.session_state.picked_suggestions = pick_suggestions(recommended_suggestions) ## add .copy() to make the code more secure in case we add things in the future

# Get suggestions from session state
suggestion, suggestion2, suggestion3 = st.session_state.picked_suggestions

# Title and button stickiness
st.title(':orange[cal.1] conversation :calendar:')

@st.cache_resource
def init_llm():
    return llm_service.init_llm()

llm = init_llm()

# Define buttons in columns
col1, col2, col3 = st.columns(3)
with st.container():
    with col1:
        button1 = st.button(suggestion)
    with col2:
        button2 = st.button(suggestion2)
    with col3:
        button3 = st.button(suggestion3)

#Start Log in state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    
# Check if the user is authorized using cookies
if not st.session_state.logged_in and cookies.get('authorized') == 'true':
    st.session_state.logged_in = True


query_params = st.query_params
if 'authorized' in query_params and not st.session_state.logged_in:
    st.session_state.logged_in = True
    cookies['authorized'] = 'true'
    st.sidebar.success("Authorization successful. You can now fetch calendar events.")
    st.query_params = {}

cookies.save()

with st.sidebar:
    st.title(":orange[Gcal] Login")
    if not st.session_state.logged_in:
        if st.button('Authorize Google Calendar'):
            auth_url = initiate_authorization()
            st.markdown(f"""
                <meta http-equiv="refresh" content="0; url={auth_url}">
                If you are not redirected automatically, <a href="{auth_url}">click here</a>.
            """, unsafe_allow_html=True)
    else:
        st.success("Logged in to Google Calendar")
        response = requests.get("http://localhost:5000/get_credentials")
        response = response.json()
        st.success(response)
        if st.button('Logout'):
            cookies['authorized'] = 'false'
            cookies.save()
            st.session_state.logged_in = False
            st.rerun()

# Start state for chat responses
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Check if prompt is present and if button is pressed
prompt = st.chat_input("How can I help you today?")

if button1:
    prompt = suggestion
elif button2:
    prompt = suggestion2
elif button3:
    prompt = suggestion3

# Store prompt in state
if prompt:
    with st.chat_message("User", avatar="📆"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Chatbot response
    response = llm_service.chat(prompt, llm)
    function_to_call = response["function_to_call"]
    del response['function_to_call']
    # output = calendar.create_event(api_types=['google'], event=response)
    with st.chat_message("Assistant", avatar="🤖"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

# Check if state log matches expected response
##st.write(st.session_state.messages,st.session_state.picked_suggestions)

