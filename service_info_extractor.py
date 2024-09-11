from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_openai import ChatOpenAI
import streamlit as st
import re
import os


def get_the_conversation(response):
    chat_history = st.session_state['chat_history']
    previous_response = ""
    if 'previous_response' not in st.session_state:
        st.session_state['previous_response'] = response
    else:
        previous_response = st.session_state['previous_response']
        st.session_state['previous_response'] = response
    index = 0
    conversation = ""
    if re.search(".*(provide|create|enter).*[Pp]assword", previous_response):
        for msg in chat_history:
            if index % 2 == 0:
                conversation += "user: " + msg + "\n"
            else:
                conversation += "assistant: " + msg + "\n"
            index += 1
    return conversation


def get_service_info(response):
    conversation = get_the_conversation(response)
    print(conversation)
    service_name = ""
    example_service_dic = """
                            {    "service_name": "value",
                                "parameters": {
                                    "username": "value",
                                    "password": "value"
                                    }
                            }
                            """
    if conversation != "":
        prompt = f"""
            Given the following conversation between an user and its assistant return the name
            of the service and its parameters and values in a dictionary format.
            MAKE SURE THAT YOU FOLLOW THE DICTIONARY FORMAT IN YOUR RESPONSE.
            HERE IS AN EXAMPLE {example_service_dic}
           
            the conversation is here:
            {conversation}
            Be concise.
            """
        print("prompt******************", prompt)
        #llm = ChatNVIDIA(model="mistralai/mixtral-8x22b-instruct-v0.1", temperature=0)
        llm = ChatOpenAI(
            openai_api_base="https://api.groq.com/openai/v1",
            openai_api_key=os.environ['GROQ_API_KEY'],
            model_name="llama-3.1-70b-versatile",
            temperature=0,
            max_tokens=1000,
        )
        response = llm.invoke(prompt)
        service_name = response.content
        print("response----------------------------", response.content)
    return service_name
