import re

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
import streamlit as st
import service_info_extractor as serv_ext
from login_process_handler import process_login
from registration_process_handler import create_new_account
import ast
import os

AI_ERROR_MSG = "Error while calling the AI model, the server might be down. Try again later"
PARSING_SERVICE_INFO_ERROR_MSG = "Error while parsing the service info details. Say hi to restart"


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
               
               FOR THE login SERVICE, MAKE SURE THAT THE USER HAS PROVIDED: username and password.
               
               And for the user registration service please guide the user through these steps:
               Request Username: Ask for their desired username.
               Request First Name: Ask for their first name.
               Request Last Name: Request their last name.
               Request Email: Request their email.
               Request Phone Number: Ask for their phone number.
               Request Home Address: ask for their home address.
               Request Password: Finally, prompt them to create a secure password.
               FOR THE registration SERVICE, MAKE SURE THAT THE USER HAS PROVIDED: in the following order:
               username, first name, last name, email, phone number, home address and password.
               
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
        if m != "":
            if count % 2 == 0:
                output = st.chat_message("user")
                output.write(m)
            else:
                output = st.chat_message("assistant")
                output.write(m)
        count += 1


def get_the_model(prompt):
    memory = ConversationBufferMemory(memory_key="chat_history")

    #llm = ChatNVIDIA(model="nv-mistralai/mistral-nemo-12b-instruct", temperature=0)
    llm = ChatOpenAI(
        openai_api_base="https://api.groq.com/openai/v1",
        openai_api_key=os.environ['GROQ_API_KEY'],
        model_name="llama-3.1-70b-versatile",
        temperature=0,
        max_tokens=1000,
    )

    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=memory,
    )
    return llm_chain


def retrieve_service_info(serv_info):
    print("retrieve_service_info************************ ", serv_info)
    try:
        service_info_dict = ast.literal_eval(serv_info)
        if isinstance(service_info_dict, dict):
            return service_info_dict
        else:
            print("The string does not represent a dictionary.")
    except (ValueError, SyntaxError) as e:
        print("Error parsing string:", e)
    return {}


def reset_chat_history(result):
    chat_history = []
    st.session_state['chat_history'] = chat_history
    chat_history.extend(["", result])
    st.session_state['previous_response'] = ""


input = st.chat_input("Say hi to start a new conversation")
if input:
    welcome_prompt = get_the_welcome_prompt(input)
    llm_chain = get_the_model(welcome_prompt)
    response = llm_chain.predict(human_input=input)
    chat_history = st.session_state['chat_history']
    chat_history.extend([input, response])
    service_info = ""
    try:
        service_info = serv_ext.get_service_info(response)
    except Exception as ex:
        reset_chat_history(AI_ERROR_MSG)
        print("Error while calling the model", ex)

    print("service_info = ", service_info)
    if service_info != "":
        service_info_dict = retrieve_service_info(service_info)
        print("service_info_dict ", service_info_dict)
        if service_info_dict:
            service_name = service_info_dict["service_name"]
            if re.search("[Ll]ogin", service_name):
                result = process_login(service_info_dict)
                reset_chat_history(result)
            else:
                result = create_new_account(service_info_dict)
                reset_chat_history(result)

        else:
            reset_chat_history(PARSING_SERVICE_INFO_ERROR_MSG)

    display_chat_history()
