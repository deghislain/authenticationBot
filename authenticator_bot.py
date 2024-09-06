import re

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import streamlit as st
import service_info_extractor as serv_ext
from login_process_handler import process_login
import ast


def get_the_welcome_prompt(human_input):
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    chat_history = st.session_state['chat_history']
    template = f"""
               You are chatbot responsible for managing the user authentication process.
               You provide the following 2 services:
               1-login service
               2-user registration service
               
               You start welcoming the user, provide a list of your services, then you ask what you can do for him. 
               
               For the loging service follow these steps:
               Request Username: Start by asking the user to provide their username.
               Request Password: Once the username is provided, ask the user to enter their password.
               
               And for the user registration service please guide the user through these steps:
               Request Username: Ask for their desired username.
               Request First Name: Ask for their first name.
               Request Last Name: Request their last name.
               Request Email: Collect their email address.
               Request Phone Number: Ask for their phone number.
               Request Address: ask for their address.
               Request Address: Finally, prompt them to create a secure password.
               
               Ensure a smooth user experience by providing clear instructions and feedback throughout the process.
               Be concise.

           {chat_history}
           Human: {human_input}
           Chatbot:"""

    return PromptTemplate(input_variables=["chat_history", "human_input"], template=template)


def display_chat_history():
    chat_history = st.session_state['chat_history']
    count = 0
    for m in chat_history:
        if count % 2 == 0:
            output = st.chat_message("user")
            output.write(m)
        else:
            output = st.chat_message("assistant")
            output.write(m)
        count += 1


def get_the_model(prompt):
    memory = ConversationBufferMemory(memory_key="chat_history")

    llm = ChatNVIDIA(model="nv-mistralai/mistral-nemo-12b-instruct", temperature=0)

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )
    return llm_chain


def parse_service_info(serv_info):
    try:
        service_info_dict = ast.literal_eval(serv_info)
        if isinstance(service_info_dict, dict):
            return service_info_dict
        else:
            print("The string does not represent a dictionary.")
    except (ValueError, SyntaxError) as e:
        print("Error parsing string:", e)
    return {}


input = st.chat_input("Say hi to start a new conversation")
if input:
    welcome_prompt = get_the_welcome_prompt(input)
    llm_chain = get_the_model(welcome_prompt)
    response = llm_chain.predict(human_input=input)
    chat_history = st.session_state['chat_history']
    chat_history.extend([input, response])
    service_info = serv_ext.get_service_info()
    if service_info != "":
        service_info_dict = parse_service_info(service_info)
        service_name = service_info_dict["service"]
        if re.search("[Ll]ogin", service_name):
            result = process_login(service_info_dict)
            chat_history.extend([input, result])

    display_chat_history()
