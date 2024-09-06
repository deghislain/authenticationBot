import streamlit as st


def get_the_conversation():
    chat_history = st.session_state['chat_history']
    index = 0
    conversation = ""
    if len(chat_history) >= 5:
        for msg in chat_history:
            if index % 2 == 0:
                conversation += "user: " + msg + "\n"
            else:
                conversation += "assistant: " + msg + "\n"
            index += 1
    return conversation
