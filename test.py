from langchain_groq import ChatGroq
from langchain_core.tools import tool
import os


model_name = "llama-3.1-70b-versatile"
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model=model_name)

def extract_username():
    """
      Extract username from the chat history.
    """
