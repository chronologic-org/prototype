import streamlit as st

#LLM API KEY

#if "chronologic_model" not in st.session_state:
    #st.session_state.chronologic_model = "name_of_llm"

##title and button stikiness
st.title(':orange[cal.1] conversation :calendar:')

suggestion = "is john free on friday?" #randomize all suggestions from a list - directly calls the function
suggestion2 = "set a meeting at 2pm"
suggestion3 = "Clear my sunday"
col1, col2, col3 = st.columns(3)
with st.container():
    with col1:
        button1 = st.button(suggestion)
    with col2:
        button2 = st.button(suggestion2)
    with col3:
        button3 = st.button(suggestion3)

##Start state
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

##check if prompt present and if button is pressed
prompt = st.chat_input("How can I help you today?")

if button1 == True:
    prompt = suggestion
elif button2 == True:
    prompt = suggestion2
elif button3 == True:
    prompt = suggestion3


##stores prompt in state
if prompt:
    #Change user as a variable depending on which user is using the app
    #user: User_name
    with st.chat_message("User", avatar="📆"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    ##Chatbot response
    #Put LLM functionality here
    response = f"Echo: {prompt}"
    with st.chat_message("Assistant", avatar="🤖"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

##check if state log matches expected response
#st.write(st.session_state.messages)







#work on LLM prompt in mixtral