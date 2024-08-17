import random
import streamlit as st
import requests

def initiate_authorization():
    auth_url = 'http://localhost:5000/authorize/google'
    st.markdown(f"""
        <meta http-equiv="refresh" content="0; url={auth_url}">
        If you are not redirected automatically, <a href="{auth_url}">click here</a>.
    """, unsafe_allow_html=True)
    
def get_token_from_url():
    query_params = st.query_params
    token = query_params.get('token', None)
    if token:
        st.session_state['token'] = token
        st.query_params.clear()
        
# Function to get the user's prompt and send it to the LLM via the Flask API
def send_prompt_to_llm(prompt):
    api_url = 'http://localhost:5000/chat'  # Replace with your actual API URL
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(api_url, json={'prompt': prompt}, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Failed to communicate with the server')
        return None

def calendar_interaction(event, function_to_call):
    api_url = f'http://localhost:5000/{function_to_call}'
    headers = {'Content-Type': 'application/json', 'Authorization': f"Bearer {st.session_state['token']}"}
    response = requests.post(api_url, json={'event': event}, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        st.error('Failed to communicate with the server')
        return None

def get_events():
    headers = {'Authorization': f"Bearer {st.session_state['token']}"}
    response = requests.get('http://localhost:5000/calendar', headers=headers)
    if response.status_code == 200:
        events = response.json()
        for event in events:
            st.write(event['summary'])
    else:
        st.error('Failed to retrieve events')

if 'token' not in st.session_state:
    get_token_from_url()

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

if 'token' in st.session_state:
    # st.button('Get Google Calendar Events', on_click=get_events)
    col1, col2, col3 = st.columns(3)
    with st.container():
        with col1:
            button1 = st.button(suggestion)
        with col2:
            button2 = st.button(suggestion2)
        with col3:
            button3 = st.button(suggestion3)

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
        response = send_prompt_to_llm(prompt)
        with st.chat_message("Assistant", avatar="🤖"):
            st.markdown(response)
        function_to_call = response['function_to_call']
        # Remove the function_to_call key from the response
        response = {key: value for key, value in response.items() if key != 'function_to_call'}        
        response = calendar_interaction(event=response, function_to_call=function_to_call)
        
        # response = {item for item in response if item != 'function_to_call'}
        # calendar_service.create_event(api_type='google', event=response)
        with st.chat_message("Assistant", avatar="🤖"):
            st.markdown(response['message'])
        st.session_state.messages.append({"role": "assistant", "content": response})



with st.sidebar:
    if 'token' in st.session_state:
        st.write('Logged in to Google Calendar') 
        if st.button('Logout'):
            st.session_state.pop('token')
            st.query_params.clear()
            st.rerun()
    else:
        st.write('Log in to Google Calendar')
        if st.button('Login'):
            initiate_authorization()