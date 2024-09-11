import streamlit as st
from cv2 import VideoCapture, imwrite
from UserManagmentSys.User import User
import uuid
import utilities as util
import requests
import json

create_microservice_url = "http://127.0.0.1:8080/create"
username_microservice_url = "http://127.0.0.1:8080/username"

MISSING_REQUIRED_INFO = "Some required information are missing"
SUCCESSFUL_MSG = "Success"
REGISTRATION_ERROR_MSG = "Error during the registration process. Please, try again later"


def capture_user_picture():
    try:
        cam = VideoCapture(0)
        result, image = cam.read()
        if result:
            username = st.session_state['username']
            imwrite(f"UserManagmentSys/images/{username}.png", image)
            st.session_state['process_status'] = 6
            return True
        else:
            return False
    except Exception as ex:
        chat_history = st.session_state['chat_history']
        chat_history.extend([input, "Error while capturing your image. Please ensure that your camera is activated,"
                                    "and that you are looking directly at it before attempting again"])
        print("Error while capturing your image", ex)


def store_user(user):
    json_user = json.dumps(user.__dict__)
    newHeaders = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    result = requests.post(create_microservice_url, json_user, headers=newHeaders)
    return result


def create_new_account(registration_info):
    print("create_new_account START")
    username = registration_info["parameters"]["username"]
    first_name = registration_info["parameters"]["first_name"]
    last_name = registration_info["parameters"]["last_name"]
    email = registration_info["parameters"]["email"]
    phone_number = registration_info["parameters"]["phone_number"]
    home_address = registration_info["parameters"]["home_address"]
    password = registration_info["parameters"]["password"]

    if username and password and first_name and last_name and email and phone_number and home_address:
        hash_password = util.hash_password(password)
        user_id = uuid.uuid4()
        user = User(str(user_id), username, hash_password, first_name, last_name, email, phone_number, home_address)

        if capture_user_picture() and store_user(user).status_code == 200:
            return SUCCESSFUL_MSG
        else:
            return REGISTRATION_ERROR_MSG

    else:
        return MISSING_REQUIRED_INFO
