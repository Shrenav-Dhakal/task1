import streamlit as st
import json
import os
from dotenv import load_dotenv
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

with open('config.json', 'r') as f:
    config = json.load(f)

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

def format_data(data):
    formatted_data = ""
    for key, value in data.items():
        formatted_data += f"{key}: {value}\n"
    return formatted_data

def submit_form(data, form_type):
    try:
        formatted_data = format_data(data)
        send_mail(formatted_data, f"{form_type} Submission")
        st.success("Form submitted successfully!")
    except Exception as e:
        st.error(f"Error submitting form: {str(e)}")
        send_mail(str(e), "Error in Form Submission")

def main():
    st.title(config['chatbot_title'])

    form_choice = st.selectbox("Choose Form", list(config['forms'].keys()))

    selected_form = config['forms'][form_choice]

    st.subheader(selected_form['form_name'])

    form_data = {}
    for field in selected_form['fields']:
        if field['type'] == 'text':
            field_value = st.text_input(field['label'])
        elif field['type'] == 'dropdown':
            field_value = st.selectbox(field['label'], field['options'])
        
        form_data[field['label']] = field_value

    if st.button("Submit"):
        submit_form(form_data, selected_form['form_name'])

    if st.button("Restart"):
        main()

if __name__ == "__main__":
    main()
