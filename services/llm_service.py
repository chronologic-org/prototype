from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def init_llm():
    llm = ChatGroq(
        temperature=0.7,
        model='mixtral-8x7b-32768',
        api_key=os.getenv('GROQ_API_KEY'),
    )
    
    structured_llm = llm.with_structured_output(method="json_mode")
    return structured_llm

def chat(prompt: str, llm: ChatGroq):
    system = """
    You are a general information agent that has access to functions to provide additional data to you. Check the input that you receive from the user, extract any key entities you need.

    If you do not have enough information in the prompt DO NOT make up an answer, instead look at the list of functions you can call to provide the information you need to answer the user's question.

    Use current date and time as default unless mentioned otherwise: 7/16/2024 6:04PM

    You have access to the following list of functions that you can call:
    {{
    delete_event(self, api_types, event_name)
    update_event(self, api_types, event_name, updated_event)
    create_event(self, api_types, event)
    }}

    You MUST provide your response in the following JSON Schema below depending on what you think the user is trying to do. If you are not given enough information for a certain portion of the JSON Schema leave it blank. You MUST take the types of the OUTPUT SCHEMA into account and adjust your provided text to fit the required types:

    Here is the OUTPUT SCHEMA for creating and updating an event:
    {{
    "function_to_call": "",
    "summary": "",
    "location": "",
    "description": ".",
    "start": {{
        "dateTime": "",
        "timeZone": ""
    }},
    "end": {{
        "dateTime": "",
        "timeZone": ""
    }},
    "recurrence": [
        "RRULE:FREQ=;COUNT="
    ],
    "attendees": [
        {{"email": ""}},
    ],
    "reminders": {{
        "useDefault": true,
        "overrides": [
        {{"method": "", "minutes": 0}}
        ]
    }}
    }}

    Here is the OUTPUT SCHEMA for deleting an event:
    {{
    "function_to_call": "",
    "summary": ""
    }}
    """

    human = "{text}"
    ai = '```json \n'
    prompt_template = ChatPromptTemplate.from_messages([("system", system), ("human", human), ("ai", ai)])

    chain = prompt_template | llm
    output = chain.invoke({"text": prompt})
    return output
    
if __name__ == '__main__':
    llm = init_llm()
    user_input = input("Enter your prompt: ")
    chat(user_input, llm)

