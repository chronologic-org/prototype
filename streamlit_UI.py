import streamlit as st
import requests

def get_token_from_url():
    query_params = st.experimental_get_query_params()
    token = query_params.get('token', [None])[0]
    if token:
        st.session_state['token'] = token

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

if 'token' in st.session_state:
    st.button('Get Google Calendar Events', on_click=get_events)
else:
    st.markdown("[Login with Google](http://localhost:5000/authorize/google)")
