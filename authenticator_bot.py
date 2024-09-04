from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from langchain_nvidia_ai_endpoints import ChatNVIDIA
import streamlit as st
import re


login_microservice_url = "http://127.0.0.1:8080/login"

def get_the_welcome_prompt(human_input):
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    chat_history = st.session_state['chat_history']
    template = f"""
               You are chatbot responsible for managing the user authentication process.
               You start welcoming the user, provide a list of your services, then you ask what you can do for him. 
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


def select_process(input):
    if re.search('login', input):
        return "login"
    elif re.search('(new account|register)', input):
        return "registration"


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


def get_the_conversation():
    chat_history = st.session_state['chat_history']
    index = 0
    conversation = ""
    if len(chat_history) >= 3:
        for msg in chat_history:
            if index % 2 == 0:
                conversation += msg + "\n"
            else:
                conversation += msg + "\n"
            index += 1
    return conversation


def get_the_service_name():
    conversation = get_the_conversation()
    print(conversation)
    if conversation != "":
        prompt = f"""
            Given the following conversation between an user and its assistant return the name
            of the service that the user is looking for.
            
            the conversation is here:
            {conversation}
            You must only return the name of the service.
            """
        print("prompt******************", prompt)
        llm = ChatNVIDIA(model="mistralai/mixtral-8x22b-instruct-v0.1", temperature=0)
        response = llm.invoke(prompt)
        print("response----------------------------", response.content)


input = st.chat_input("Say hi to start a new conversation")
if input:
    welcome_prompt = get_the_welcome_prompt(input)
    llm_chain = get_the_model(welcome_prompt)
    response = llm_chain.predict(human_input=input)
    chat_history = st.session_state['chat_history']
    chat_history.extend([input, response])
    get_the_service_name()
    display_chat_history()
