import streamlit as st
import re
import os
from dotenv import load_dotenv
import json
import smtplib
import email.message


load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
SMTP_HOST= os.getenv('SMTP_HOST')
SMTP_PORT= os.getenv('SMTP_PORT')
TO_EMAIL= os.getenv('EMAIL_TO')
EMAIL = os.getenv("EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

import timeit
import time


def send_mail(Content, subject):
    try:
        msg = email.message.Message()
        msg['Subject'] = f"{subject}"
        msg['FROM'] =  EMAIL
        msg['To'] = TO_EMAIL
        msg.add_header("Content-Type", 'text/html')
        msg.set_payload(f'{Content}')
        smtp = smtplib.SMTP(SMTP_HOST,SMTP_PORT)
        smtp.starttls()
        smtp.login(EMAIL,EMAIL_PASSWORD)
        smtp.sendmail(msg['From'], [msg['To']], msg.as_string())
        smtp.quit()
        print("Succesfully send")
    except Exception as e:
        st.write("Error: cannot send mail")

def main():
    st.title("Simple Form using st.form()")

    with st.form(key='my_form'):
        # Text Input
        firstname = st.text_input("Enter the First name of the student:")
        lastname = st.text_input("Enter the Last name of the student:")
        age = st.number_input("Enter the age:", min_value=0, max_value=150, step=1)
        gender = st.radio("Select Gender : ", ("Male", "Female", "Other"))
        student_dob = st.date_input("Select student date of birth:")
        phoneno = st.text_input("Enter Phone number of Student:")
        gmail = st.text_input("Enter Email address Student:")
        student_course = st.selectbox("Select student course:", ["Mathematics", "Science", "History", "Account", "Computer Science"])
        # Button to submit the form
        data = {
                    'firstname':firstname,
                    'lastname':lastname,
                    'age':age,
                    'email':gmail,
                    'gender':gender,
                    'dob':student_dob,
                    'phone':phoneno,
                    'course':student_course
                }
        submitted = st.form_submit_button("Submit",on_click=click(data))


def click(data):
    time.sleep(5)
    send_mail(data,"Student Registration")
    st.write("Success")
    
    
