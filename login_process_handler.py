import ast

import cv2
import streamlit as st
from cv2 import VideoCapture
from skimage.metrics import structural_similarity as ssim
import requests
from utilities import hash_password

login_microservice_url = "http://127.0.0.1:8080/login"

IMAGE_ISSUES_MSG = ("You did not pass the image verification process. Please ensure that your camera is activated,"
                    "and that you are looking directly at it before attempting again")

CREDENTIALS_ERROR_MSG = "Invalid username or password"
AUTHENTICATION_ERROR_MSG = "Error during the authentication process. Please, try again later"
SUCCESSFUL_MSG = "Success"


def image_verification():
    if 'image_similarity' in st.session_state and st.session_state['image_similarity'] > 0.60:
        return True

    cam = VideoCapture(0)
    result, image = cam.read()
    if result:
        local_image = cv2.imread("UserManagmentSys/images/armel.png")
        s = ssim(local_image, image, channel_axis=2)
        print("similarity  ", s)
        if s > 0.60:
            if 'image_similarity' not in st.session_state:
                st.session_state['image_similarity'] = s
            return True

    return False


def user_authentication(username, password):
    hashed_password = hash_password(password)
    response = requests.get(login_microservice_url,
                            json={'username': f"""{username}""", 'password': f"""{hashed_password}"""})
    return response


def process_login(login_info_dict):
    print("process_login START")
    if image_verification():
        username = login_info_dict["parameters"]["username"]
        password = login_info_dict["parameters"]["password"]
        if username and password:
            try:
                response = user_authentication(username, password)
                if response.status_code == 200:
                    return SUCCESSFUL_MSG
                else:
                    return CREDENTIALS_ERROR_MSG
            except Exception as ex:
                print("An error occurred during your login", ex)
                return AUTHENTICATION_ERROR_MSG
        else:
            return CREDENTIALS_ERROR_MSG
    else:
        return IMAGE_ISSUES_MSG
