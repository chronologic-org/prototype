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


with st.sidebar:
    if 'token' in st.session_state:
        st.write('Logged in to Google Calendar') 
        if st.button('Logout'):
            st.session_state.pop('token')
            st.query_params.clear()
    else:
        st.write('Log in to Google Calendar')
        if st.button('Login'):
            initiate_authorization()