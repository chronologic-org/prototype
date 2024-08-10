import streamlit as st
import requests

# Function to initiate authorization
def initiate_authorization():
    return 'http://localhost:5000/authorize/google'

# Check if the user is authorized
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Handle query parameters
if 'authorized' in st.experimental_get_query_params():
    st.session_state.logged_in = True
    st.experimental_set_query_params()  # Clear query params

# Function to check authorization and fetch credentials
def check_authorization():
    st.write("Checking authorization status...")
    response = requests.get("http://localhost:5000/get_credentials", cookies=requests.utils.dict_from_cookiejar(st.session_state.get('cookies', requests.cookies.RequestsCookieJar())))
    st.write("Response status code:", response.status_code)
    st.write("Response content:", response.content)
    if response.status_code == 200:
        credentials = response.json()
        st.json(credentials)
    else:
        st.error("Failed to get credentials")

# Sidebar layout for login and logout
with st.sidebar:
    if st.session_state.logged_in:
        st.success("Logged in to Google Calendar")
        if st.button('Check Authorization and Fetch Credentials'):
            check_authorization()
        if st.button('Logout'):
            st.session_state.logged_in = False
            st.session_state.cookies = requests.cookies.RequestsCookieJar()
            st.experimental_rerun()
    else:
        st.title("Gcal Login")
        if st.button('Authorize Google Calendar'):
            auth_url = initiate_authorization()
            st.markdown(f"""
                <meta http-equiv="refresh" content="0; url={auth_url}">
                If you are not redirected automatically, <a href="{auth_url}">click here</a>.
            """, unsafe_allow_html=True)

# Fetch calendar events if logged in
if st.session_state.logged_in:
    st.write("Fetching calendar events...")
    response = requests.get("http://localhost:5000/calendar", cookies=requests.utils.dict_from_cookiejar(st.session_state.get('cookies', requests.cookies.RequestsCookieJar())))
    st.write("Response status code:", response.status_code)
    st.write("Response content:", response.content)
    if response.status_code == 200:
        events = response.json()
        st.write(events)
    else:
        st.error("Failed to fetch calendar events")

# Capture cookies after authorization
if 'Set-Cookie' in st.experimental_get_query_params():
    st.session_state.cookies = requests.cookies.cookiejar_from_dict(st.experimental_get_query_params()['Set-Cookie'])
    st.experimental_set_query_params()  # Clear query params
