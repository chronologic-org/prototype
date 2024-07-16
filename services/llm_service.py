from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    temperature=0.7,
    model='mixtral-8x7b-32768',
    api_key= os.getenv('GROQ_API_KEY'), 
)

system = "You are a helpful assistant."
human = "{text}"
prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

chain = prompt | llm
output = chain.invoke({"text": "Explain the importance of low latency for LLMs."})
print(output)