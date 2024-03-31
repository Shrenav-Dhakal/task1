import streamlit as st
import re
import os
from dotenv import load_dotenv
import json
import smtplib
import email.message
from student import main,send_mail
from hospital import hospital
load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def main1():
    st.header("Chat Bot Registration")
    model = genai.GenerativeModel("gemini-pro")
    user_input = st.text_input("Ask us a question (Type 'form' for registration):")

    submit = st.button("Generate")
    if submit:
        if "form student" in user_input:
            main()
        elif "form hospital" in user_input:
            hospital()
        else:
            response = model.generate_content(user_input)
            st.write(response.text)

if __name__ == "__main__":
    main1()
