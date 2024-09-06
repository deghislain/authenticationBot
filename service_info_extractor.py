from langchain_nvidia_ai_endpoints import ChatNVIDIA
import utilities as util


def get_service_info():
    conversation = util.get_the_conversation()
    print(conversation)
    service_name = ""
    if conversation != "":
        prompt = f"""
            Given the following conversation between an user and its assistant return the name
            of the service that the user is looking for with its parameters and values in a dictionary format.
            
            the conversation is here:
            {conversation}
            Be concise.
            """
        print("prompt******************", prompt)
        llm = ChatNVIDIA(model="mistralai/mixtral-8x22b-instruct-v0.1", temperature=0)
        response = llm.invoke(prompt)
        service_name = response.content
        print("response----------------------------", response.content)
    return service_name
